class UnionMobilizationTaskConfig:
    """
    联盟总动员任务配置类
    """

    def __init__(self, task_type, execution_logic_enabled=True, execution_logic=None, time_limit=None):
        """
        初始化任务配置

        Args:
            task_type (str): 任务类型 ("exclusive_training", "public_training", "public_rally", etc.)
            execution_logic_enabled (bool): 是否启用该任务配置
            execution_logic (str): 执行逻辑类型
            time_limit (int|None): 时间限制（分钟）
        """
        self.task_type = task_type  # 任务类型
        self.execution_logic_enabled = execution_logic_enabled  # 是否启用执行逻辑
        self.execution_logic_enabled = execution_logic  # 执行逻辑
        self.time_limit = time_limit  # 时间限制（分钟）
        self.custom_params = {}  # 自定义参数

    def matches_task(self, task):
        """
        检查任务是否匹配此配置

        Args:
            task (object): 任务对象

        Returns:
            bool: 是否匹配
        """
        # 根据任务类型和特征匹配逻辑
        pass

    def should_execute(self, task_context):
        """
        根据任务上下文判断是否应该执行

        Args:
            task_context (dict): 任务上下文信息

        Returns:
            bool: 是否应该执行
        """
        if not self.execution_logic_enabled:
            return False

        # 根据不同的执行逻辑判断
        if self.execution_logic_enabled == "exclusive_training":
            # 专属任务训练士兵：最短时间小于等于30分钟
            min_training_time = task_context.get("min_training_time", float('inf'))
            return min_training_time <= (self.time_limit or 30)

        elif self.execution_logic_enabled == "public_training":
            # 公共任务训练士兵：当前没有接受任务且最短时间小于等于60分钟
            has_current_task = task_context.get("has_current_task", False)
            min_training_time = task_context.get("min_training_time", float('inf'))
            return (not has_current_task) and min_training_time <= (self.time_limit or 60)

        elif self.execution_logic_enabled == "public_rally":
            # 公共任务集结：当前没有接受任务
            has_current_task = task_context.get("has_current_task", False)
            return not has_current_task

        return False


# 全局配置列表示例
union_mobilization_configs = [
    # 专属任务训练士兵配置
    UnionMobilizationTaskConfig(
        task_type="exclusive_training",
        execution_logic_enabled=True,
        execution_logic="exclusive_training",
        time_limit=30  # 30分钟限制
    ),

    # 公共任务训练士兵配置
    UnionMobilizationTaskConfig(
        task_type="public_training",
        execution_logic_enabled=True,
        execution_logic="public_training",
        time_limit=60  # 60分钟限制
    ),

    # 公共任务集结配置
    UnionMobilizationTaskConfig(
        task_type="public_rally",
        execution_logic_enabled=True,
        execution_logic="public_rally",
        time_limit=None  # 无时间限制
    )
]


def get_default_union_mobilization_config():
    """
    获取默认联盟总动员任务配置列表

    Returns:
        list: UnionMobilizationTaskConfig对象列表
    """
    # 从user_task_config获取配置
    return union_mobilization_configs
