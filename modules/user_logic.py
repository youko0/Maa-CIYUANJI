# -*- coding: utf-8 -*-
"""
用户信息相关的游戏逻辑
包含用户信息识别和动作
"""
import re
import time
from datetime import datetime, timedelta
from typing import List

from maa.define import TaskDetail, OCRResult

from core.balance_manager import BalanceInfo
from core.maa_manager import get_maa_manager
from modules.game_logger import GameLoggerFactory
from utils.time_utils import TimeUtils


class UserLogic:
    """
    用户信息相关的游戏逻辑
    包含用户信息识别和动作
    """

    def __init__(self, device_serial, user_data_updated):
        self.device_serial = device_serial
        self.maa_manager = get_maa_manager()
        self.tasker = self.maa_manager.get_device_tasker(device_serial)
        self.logger = GameLoggerFactory.get_logger(device_serial)
        self.user_data_updated = user_data_updated

    def sign_in(self, is_user_data_updated=False):
        """签到"""

        result_succeeded = self.tasker.post_task("existsAndClickUser").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[签到]没有识别到用户页")
            return False
        time.sleep(0.5)
        # 进入签到任务页面
        result_succeeded = self.tasker.post_task("existsAndClickSignInEntrance").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[签到]没有识别到签到入口按钮，判断是否存在青少年模式提示")
            # 判断是否出现了青少年模拟提示
            result_succeeded = self.tasker.post_task("existsTeenModeTips").wait().succeeded
            if result_succeeded is False:
                self.logger.error(f"[签到]没有出现青少年模式提示，任务结束")
                return False
            else:
                # 点击我知道了
                self.tasker.post_task("existsAndClickISeeBtn").wait()
                time.sleep(0.3)
                result_succeeded = self.tasker.post_task("existsAndClickSignInEntrance").wait().succeeded
                if result_succeeded is False:
                    self.logger.error(f"[签到]没有识别到签到入口按钮，任务结束")
                    return False

        # 等待页面加载结束（判断是否成功进入签到成功页面）
        result_succeeded = self.tasker.post_task("existsRulesDescription").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[签到]没有正常进入签到成功页面")
            return False

        self.logger.info(f"[签到]成功进入签到成功页面")
        # 判断是否存在签到成功提示
        if self.tasker.post_task("existsSignInSuccessTip").wait().succeeded:
            self.logger.info('签到成功，识别代币数量')
            result = self.tasker.post_task("ocrSignInCoinNum").wait().get()
            if result and result.nodes and len(result.nodes) > 0:
                coin_num_str = result.nodes[0].recognition.best_result.text
                # 添加代币（模拟签到获得5个代币）
                expire_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                # self.config_manager.add_coin(self.device_serial, int(coin_num_str), expire_time)
                print(f"{self.device_serial}设备签到成功，添加代币：{coin_num_str}，过期时间：{expire_time}")
                # 更新设备信息及余额数据

            else:
                self.logger.error(f"{self.device_serial}设备没有识别到代币数量")
        else:
            # 签到失败
            self.logger.warning(f"[签到]设备已签到")

        # 调用返回按钮
        self.tasker.post_task("androidBack").wait()

    def refresh_balance(self):
        """刷新余额"""
        # 点击用户tabbar页
        result_succeeded = self.tasker.post_task("existsAndClickUser").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[刷新余额]没有识别到用户页")
            return False
        time.sleep(0.5)
        # 点击进入代币页面
        result_succeeded = self.tasker.post_task("existsAndClickCoinEntrance").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[刷新余额]没有识别到代币入口")
            return False
        time.sleep(0.5)
        # 识别代币总数量
        total_coin_num = 0
        result = self.tasker.post_task("ocrTotalCoinNum").wait().get()
        if result and result.nodes and len(result.nodes) > 0:
            coin_num_str = result.nodes[0].recognition.best_result.text
            total_coin_num = int(coin_num_str)
            print(f"[刷新余额]识别到设备代币总余额：{coin_num_str}")
        else:
            self.logger.error(f"[刷新余额]没有识别到代币数量")
            return
        time.sleep(0.5)
        # 点击进入代币明细页
        pipeline_override = {"existsAndClickCoinEntrance": {"target_offset": [85, 0, 16, 0]}}
        result_succeeded = self.tasker.post_task("existsAndClickCoinEntrance", pipeline_override).wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[刷新余额]没有识别到代币入口")
            return False
        time.sleep(0.5)

        # 识别代币明细
        balance_info_list = self.swipe_and_ocr_coin_detail()
        # 计算balance_info_list总余额是否等于total_coin_num
        balance = sum([item.balance for item in balance_info_list])
        if balance != total_coin_num:
            self.logger.warning(f"[刷新余额]代币明细和总余额不一致，刷新失败")
            return

    def swipe_and_ocr_coin_detail(self):
        """滑动并识别代币明细"""
        self.logger.info(f"[刷新余额]开始识别代币明细")
        balance_info_list = []
        while True:
            find_goods_list_result = self.tasker.post_task("ocrCoinDetails").wait().get()
            if find_goods_list_result and len(find_goods_list_result.nodes) > 0:
                ocr_result_list = find_goods_list_result.nodes[0].recognition.filterd_results
                balance_infos = self.parse_ocr_to_balance_info(ocr_result_list)
                # 求balance_infos较balance_info_list的差集
                balance_infos = [item for item in balance_infos if item not in balance_info_list]
                if balance_infos:
                    balance_info_list.extend(balance_infos)
                else:
                    break
            # 滑动屏幕翻页
            self.tasker.controller.post_swipe(324, 1195, 317, 275, 1200).wait()
            time.sleep(0.2)

        return balance_info_list

    def parse_ocr_to_balance_info(self, ocr_results: List[OCRResult]) -> List[BalanceInfo]:
        """
        解析OCR结果列表为BalanceInfo对象列表

        规律:
        一组完整的BalanceInfo对象由以下元素组成：
        - "余额"和"代币"标签
        - 余额数量（数字）
        - 代币数量（以"总额"开头的文本）
        - 过期时间（以"有效期"开头的文本）
        - 可选状态："已过期"、"已使用"，如果出现这些状态，则表示该BalanceInfo不是有效的

        各元素的顺序是不固定的，需要动态匹配。
        """
        balance_infos = []
        i = 0

        while i < len(ocr_results):
            # 如果遇到"已过期"或"已使用"，则停止解析
            if ocr_results[i].text in ["已过期", "已使用"]:
                break

            # 查找一个完整的BalanceInfo组
            if ocr_results[i].text == "余额":
                # 寻找关联的元素，最多查找接下来的10个元素
                group_elements = [ocr_results[i]]  # 包含起始的"余额"
                j = i + 1
                while j < len(ocr_results) and j < i + 11:
                    # 如果遇到"已过期"或"已使用"或其他"余额"，则结束当前组
                    if ocr_results[j].text in ["已过期", "已使用", "余额"]:
                        break
                    group_elements.append(ocr_results[j])
                    j += 1

                # 从group_elements中提取所需信息
                amount = 0  # 代币数量
                balance = 0  # 余额数量
                expire_time = ""

                # 查找余额数量（数字）
                for element in group_elements:
                    if element.text.isdigit():
                        balance = int(element.text)
                        break

                # 查找代币数量（以"总额"开头的文本）
                for element in group_elements:
                    if element.text.startswith("总额"):
                        amount_text = element.text.replace("总额", "")
                        if amount_text.isdigit():
                            amount = int(amount_text)
                        break

                # 查找过期时间（以"有效期"开头的文本）
                for element in group_elements:
                    if element.text.startswith("有效期"):
                        expire_time = element.text.replace("有效期", "")
                        # 处理日期格式问题，添加空格分隔符
                        if "00:00:00" in expire_time and " 00:00:00" not in expire_time:
                            expire_time = expire_time.replace("00:00:00", " 00:00:00")
                        break

                # 只有当找到必要信息时才创建BalanceInfo对象
                if amount > 0 or balance > 0 or expire_time:
                    # 创建BalanceInfo对象
                    balance_info = BalanceInfo(
                        amount=amount,
                        balance=balance,
                        expire_time=expire_time
                    )

                    balance_infos.append(balance_info)

                # 移动索引到下一组
                i = j

            else:
                i += 1

        return balance_infos
