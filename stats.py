"""第3—4天练习区。保留函数名和返回字段，内部实现由你完成。"""

def summarize(tasks, keyArray=None):
    """统计任务记录，返回一个字典。
    返回字段：total / passed / failed / errors / success_rate。
    success_rate是0到1的比例，例如0.5，不是字符串"50%"。
    空列表返回：0 / 0 / 0 / 0 / None。

    id是非空字符串且不可重复；status只能为pass、fail、error。
    duration_ms必须是非负数字（不接受布尔值）。
    不合格记录抛出ValueError，提示具体字段；不要修改输入列表。

    提示：先做正常输入的计数，下一天再补校验和空列表。
    """
    if (keyArray == None):
        keyArray = ['total', 'passed', 'failed', 'errors', 'success_rate']
    emptyRet = {'total': 0, 'passed': 0, 'failed': 0, 'errors': 0, 'success_rate': None}
    if (len(tasks) == 0):
        return emptyRet
    ret = dict()
    idArray = []
    for key in keyArray:
        ret[key] = 0
    for task in tasks:
        ret['total'] += 1
        if ('id' not in task.keys() or 'status' not in task.keys() or 'duration_ms' not in task.keys()):
            raise ValueError(f'评测数据异常，每条记录必须有id、status和duration_ms，评测数据: {task}')
        if (task['id'] in idArray or len(task['id']) == 0):
            raise ValueError(f'评测数据异常，id是非空字符串且不可重复，评测数据: {task}')
        else:
            idArray.append(task['id'])
        if (type(task['duration_ms']) != int or task['duration_ms'] < 0):
            raise ValueError(f'评测数据异常，duration_ms必须是非负数字，评测数据: {task}')
        if (task['status'] == 'pass'):
            ret['passed'] += 1
        elif (task['status'] == 'fail'):
            ret['failed'] += 1
        elif (task['status'] == 'error'):
            ret['errors'] += 1
        else:
            raise ValueError(f'评测数据异常，任务状态应当为pass、fail或者error，评测数据: {task}')
    if (ret['total'] == 0):
        ret['success_rate'] == None
    else:
        rate = ret['passed'] / ret['total']
        ret['success_rate'] = float(f"{rate:.3f}")
    return ret
