# -*- coding: utf-8 -*-
"""
用户信息相关的游戏逻辑
包含用户信息识别和动作
"""
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from core.balance_manager import get_balance_manager
from core.maa_manager import get_maa_manager
from core.novel_manager import get_novel_manager
from modules.game_logger import GameLoggerFactory
from utils.maafw_utils import find_element_by_swipe
from utils.math_utils import MathUtils
from utils.random_utils import RandomUtils


class NovelLogic:
    """
    用户信息相关的游戏逻辑
    包含用户信息识别和动作
    """

    def __init__(self, device_serial):
        self.device_serial = device_serial
        self.maa_manager = get_maa_manager()
        self.novel_manager = get_novel_manager()
        self.balance_manager = get_balance_manager()
        self.tasker = self.maa_manager.get_device_tasker(device_serial)
        self.logger = GameLoggerFactory.get_logger(device_serial)

    def initialized(self):
        """初始化"""
        result_succeeded = self.tasker.post_task("existAndClickBookshelf").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别初始化]没有识别到书架页")
            return False
        time.sleep(0.6)
        # 切换书架为列表模式
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((670, 98, 24, 40))).wait()
        time.sleep(0.6)
        result_succeeded = self.tasker.post_task("existAndClickListModeBtn").wait().succeeded
        if result_succeeded is False:
            result_succeeded = self.tasker.post_task("existListGridModeBtn").wait().succeeded
            if result_succeeded:
                self.logger.error(f"[小说识别初始化]切换书架已为列表模式")
                # 消除弹框影响
                self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((670, 98, 24, 40))).wait()
                time.sleep(0.6)
            else:
                self.logger.error(f"[小说识别初始化]切换书架为列表模式失败，请重试")
                return False
        # 点击第一本小说
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((57, 363, 352, 145))).wait()
        time.sleep(0.8)
        # 点击一个中间安全的位置，调出设置按钮
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((242, 500, 237, 370))).wait()
        time.sleep(0.6)
        # 判断是否存在设置按钮
        result_succeeded = self.tasker.post_task("existAndClickSettingsBtn").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别初始化]没有识别到设置按钮")
            return False
        time.sleep(0.3)
        # 设置字体字为最小
        self.tasker.controller.post_swipe(231, 881, 33, 879, 700).wait()
        time.sleep(0.2)
        # 点击更多设置
        result_succeeded = self.tasker.post_task("existAndClickMoreSettingsBtn").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别初始化]没有识别到更多设置按钮")
            return False
        time.sleep(0.3)
        # 依次点击最窄、最窄、无、隐藏
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((50, 242, 80, 45))).wait()
        time.sleep(0.3)
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((50, 424, 80, 42))).wait()
        time.sleep(0.3)
        # self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((80,612,33,64))).wait()
        # time.sleep(0.3)
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((52, 853, 84, 45))).wait()

        # 完成初始化
        self.maa_manager.initialized_complete(self.device_serial)

        # 调用返回按钮
        self.tasker.post_task("androidBack").wait()
        # 调用返回按钮
        self.tasker.post_task("androidBack").wait()
        self.logger.info(f"[小说识别初始化]初始化完成")

    def ocr_novel(self, novel_name, chapter_list):
        """
        小说识别
        :param novel_name: 小说名称
        :param chapter_list: 章节列表（必须为连续的章节数）
        :return:
        """
        result_succeeded = self.tasker.post_task("existAndClickBookshelf").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别]没有识别到书架页")
            return False
        time.sleep(0.6)
        # 判断书架是否存在该小说
        pipeline_override = {"existAndClickNovelInBookshelf": {"expected": novel_name}}
        result_succeeded = self.tasker.post_task("existAndClickNovelInBookshelf", pipeline_override).wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别]没有在书架中识别到小说： {novel_name}，尝试进行搜索")
            result_succeeded = self._execute_search_novel(novel_name)
            if result_succeeded is False:
                return False
        time.sleep(0.6)
        # 进入目录
        # 点击一个中间安全的位置，调出目录按钮
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((242, 500, 237, 370))).wait()
        time.sleep(0.6)
        # 点击目录按钮
        result_succeeded = self.tasker.post_task("existAndClickCatalogueBtn").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别]没有找到目录按钮")
            return False
        time.sleep(0.6)
        # 开始滑动识别章节
        # chapter_name = MathUtils.pad_zero(chapter_list[0], 3)
        chapter_name = f'^(?!.*\d+年\d+月\d+日){chapter_list[0]}.*$'

        find_element = find_element_by_swipe(
            tasker=self.tasker,
            swipe_start_point=[252, 1232],
            swipe_end_point=[247, 505],
            target_pipeline="existAndClickChapter",
            pipeline_override={"existAndClickChapter": {"expected": "^" + chapter_name}},
            swipe_num=60,
            swipe_pause=0.5,
            swipe_duration=200,
            touch_pause=0.5,
            is_start_swipe_to_boundary=False
        )
        if find_element is False:
            self.logger.error(f"[小说识别]没有找到章节")
            return
        time.sleep(0.5)
        # 执行小说章节内容识别
        self._execute_ocr_novel_chapter_content(novel_name, chapter_list)

    def _execute_search_novel(self, novel_name):
        """执行小说搜索，并加入书架，调用该方法时，确保已在书架页"""
        # 点击搜索栏
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((82, 93, 472, 45))).wait()
        time.sleep(0.6)
        # 输入小说名
        pipeline_override = {"inputText": {"input_text": novel_name}}
        self.tasker.post_task("inputText", pipeline_override).wait()
        time.sleep(0.6)
        # 点击搜索按钮
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((635, 79, 47, 26))).wait()
        time.sleep(1.2)
        # 判断是否存在该小说
        pipeline_override = {"existAndClickNovelInBookshelf": {"expected": novel_name}}
        result_succeeded = self.tasker.post_task("existAndClickNovelInBookshelf", pipeline_override).wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别]没有搜索到小说： {novel_name}，请检查小说名是否正确")
            return False
        time.sleep(0.6)
        # 加入书架
        ocr_status_result = self.tasker.post_task("ocrNovelBookshelfStatus").wait().get()
        if ocr_status_result.status.succeeded:
            best_result = ocr_status_result.nodes[0].recognition.best_result
            status_text = best_result.text
            if status_text == "加入书架":
                # 点击加入书架
                self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box(best_result.box)).wait()
                time.sleep(0.3)
            else:
                self.logger.error(f"[小说识别]小说 {novel_name} 已经在书架中")

        # 点击开始阅读
        result_succeeded = self.tasker.post_task("existAndClickStartReadingBtn").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别]没有搜索到小说： {novel_name}，请检查小说名是否正确")
            return False
        return True

    def _execute_ocr_novel_chapter_content(self, novel_name, chapter_list: List):
        """执行小说章节内容识别（调用该方法时，确保已经进入阅读状态，且为开始识别的第一章）"""
        is_close_auto_buy = False  # 是否关闭了自动购买
        # 循环次数
        current_loop_num = 0
        i = 0
        # 通知类章节序号（小数点）
        chapter_notice_num = 0
        while i < len(chapter_list):
            chapter_num = chapter_list[i]
            # 识别当前章节价格
            chapter_price = 0
            ocr_result = self.tasker.post_task("ocrChapterPrice").wait().get()
            if ocr_result.status.succeeded:
                best_result = ocr_result.nodes[0].recognition.best_result
                best_result_text = best_result.text
                if best_result_text.startswith("订阅本章:"):
                    # 处理识别结果，只保留价格数字，如：订阅本章:15书币
                    chapter_price = int(best_result_text.replace("订阅本章:", "").replace("书币", ""))
                    novel_info = self.novel_manager.get_novel(novel_name)
                    # 关闭自动购买（显示章节需要购买时，自动订阅下一章是选中状态）
                    if is_close_auto_buy is False:
                        ocr_auto_buy_result = self.tasker.post_task("ocrChapterAutoBuyStatus").wait().get()
                        if ocr_auto_buy_result.status.succeeded:
                            self.logger.info(f"[小说识别]识别到自动订阅下一章为选中状态，点击关闭")
                            is_close_auto_buy = True
                            self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box(ocr_auto_buy_result.nodes[0].recognition.best_result.box)).wait()
                        else:
                            self.logger.info(f"[小说识别]没有识别到自动订阅下一章状态")

                    if novel_info.is_buy:
                        self.logger.info(f"[小说识别]识别到{chapter_num}章章节价格： {chapter_price}，执行订阅章节")
                        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box(best_result.box)).wait()
                        self.maa_manager.consume_coins(self.device_serial, novel_name, str(chapter_num), chapter_price)
                        time.sleep(3)
                    else:
                        self.logger.info(f"[小说识别]识别到{chapter_num}章章节价格： {chapter_price}，当前小说不进行订购章节")
                        break

                elif best_result_text.startswith("余额不足"):
                    self.logger.info(f"[小说识别]设备余额不足，结束识别")
                    break
            else:
                self.logger.debug(f"[小说识别]没有识别到{chapter_num}章章节价格，可能为免费章节，直接进行识别")

            # 识别章节名
            chapter_name = ""
            ocr_result = self.tasker.post_task("ocrNovelChapterName").wait().get()
            if ocr_result.status.succeeded:
                chapter_name = ocr_result.nodes[0].recognition.best_result.text
                # 判断当前章节是否为正常章节（排除通知类章节）
                if chapter_name.find(str(chapter_num)) == -1:
                    self.logger.info(f"[小说识别]识别到{chapter_num}章章节名： {chapter_name}，可能为通知类章节，当前章节不计入识别章节数")
                    i = i - 1
                    chapter_notice_num += 1
                    chapter_num = float(f"{chapter_num - 1}.{chapter_notice_num}")
                else:
                    chapter_notice_num = 0
            else:
                self.logger.info(f"[小说识别]没有识别到{chapter_num}章章节名")
                chapter_name = f"未知章节{chapter_name}"

            # 识别当前章节页码
            page_num = 1
            current_page_num = 1
            ocr_result = self.tasker.post_task("ocrChapterContentPageNum").wait().get()
            if ocr_result.status.succeeded:
                best_result_text = ocr_result.nodes[0].recognition.best_result.text
                if "/" in best_result_text:
                    page_num_arr = best_result_text.split("/")
                    page_num = int(page_num_arr[1])
                    current_page_num = int(page_num_arr[0])
            else:
                self.logger.info(f"[小说识别]没有识别到{chapter_name}章章节页码，章节可能尚未解锁")
                break

            # 识别小说内容
            novel_chapter_content = self._execute_ocr_novel_chapter_content_fun(chapter_num, page_num)
            # 保存小说内容
            novels_chapter_path = Path(f"configs/novels/{novel_name}/{chapter_num}.json")
            # 确保配置目录存在
            novels_chapter_path.parent.mkdir(parents=True, exist_ok=True)
            novel_chapter_obj = {
                "num": chapter_num,
                "name": chapter_name,
                "price": chapter_price,
                "content": novel_chapter_content,
                "device_serial": self.device_serial,
                "device_name": self.maa_manager.get_device_name(self.device_serial),
            }
            try:
                with open(novels_chapter_path, 'w', encoding='utf-8') as f:
                    json.dump(novel_chapter_obj, f, ensure_ascii=False, indent=2)
                self.logger.info(f"[小说识别]保存{chapter_name}章内容成功")
            except Exception as e:
                self.logger.error(f"保存{chapter_name}章内容失败: {e}")
            # 将当前章节页码保存到配置文件中
            if type(chapter_num) == int:
                self.novel_manager.add_complete_chapter(novel_name, chapter_num)
                # 重置当前进度
                self.novel_manager.reset_progress(novel_name)
            i = i + 1
            current_loop_num = current_loop_num + 1
            if current_loop_num > len(chapter_list) * 2:
                self.logger.info(f"[小说识别]已识别{current_loop_num}章，大于{len(chapter_list) * 2}章，中断识别")
                break

    def _execute_ocr_novel_chapter_content_fun(self, chapter_num, page_num):
        """识别小说内容方法"""
        # 识别小说内容
        novel_chapter_content = ""
        for i in range(page_num):
            is_first_line = True
            ocr_result = self.tasker.post_task("ocrNovelChapterContent").wait().get()
            if ocr_result.status.succeeded:
                line_result_list = ocr_result.nodes[0].recognition.filtered_results
                for line_result in line_result_list:
                    is_first_line = False
                    if line_result.box[0] >= 80 and is_first_line is False:
                        novel_chapter_content += "\n\t\t"
                    novel_chapter_content += line_result.text
            else:
                self.logger.error(f"[小说识别]没有识别到{chapter_num}章{i + 1}页内容")

            swipe_pipeline_override = {"swipe": {"begin": [584, 439, 1, 1],
                                                 "end": [136, 437, 1, 1],
                                                 "duration": 500}}
            self.tasker.post_task("swipe", swipe_pipeline_override).wait()
            time.sleep(0.5)
        return novel_chapter_content
