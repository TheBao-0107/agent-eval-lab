from tasks import TASKS
from stats import summarize

# 第2天：打印记录总数，逐条打印id和status。
keyArray = ['total', 'passed', 'failed', 'errors', 'success_rate']


def main():
    # print("agent-eval-lab ready")
    print(len(TASKS))
    for task in TASKS:
        print(f'{task['id']} {task['status']}')

    sumData = summarize(TASKS, keyArray)
    for key in sumData.keys():
        if (key == 'success_rate'):
            if (sumData[key] == None):
                print(f'{key}: {sumData[key]}')
            else:
                print(f'{key}: {sumData[key]:.1%}')
        else:
            print(f'{key}: {sumData[key]}')


# 第3天：from stats import summarize，调用summarize(TASKS)。
# 然后逐行输出total、passed、failed、errors、success_rate。
# 比例0.5用百分比格式显示为50.0%；None显示n/a，不做除法。
if __name__ == '__main__':
    main()
