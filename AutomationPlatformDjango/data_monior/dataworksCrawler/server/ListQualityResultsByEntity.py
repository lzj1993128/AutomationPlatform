import pandas as pd
import datetime
from data_monior.dataworksCrawler.server.Fuzzy_Match import check_type_fuzzy_match
from data_monior.models import dataworks_rule_handle



def rule_handle(CheckResult, RuleId, handle_list, new_df):
    '''

    :param CheckResult: 校验结果
    :param RuleId: 规则id
    :param handle_list: 已处理的规则id列表
    :param new_df: 获取预计处理时间
    :return:
    '''
    RuleId = str(RuleId)
    result_dict = {'handle_status': '', 'overtime': ''}
    if CheckResult != 0:
        if RuleId in handle_list:
            new_df_dict = new_df[new_df.ruleid == RuleId].to_dict(orient='records')
            result_dict['overtime'] = new_df_dict[0]['over_time']
            result_dict['handle_status'] = 1
        else:
            result_dict['handle_status'] = 0
    return result_dict


def rule_handle_status(CheckResult, RuleId, handle_list_last, bizdate):
    '''
    判断处理是否失败
    :param CheckResult:规则id
    :param RuleId:校验结果
    :param handle_list_last:取出预计处理时间在当前时间前一天的ruleid
    :param bizdate:业务日期，判断预计处理时间是否为当前时间前一天
    :return:
    '''
    RuleId = str(RuleId)
    over_time = bizdate[0:10]
    if CheckResult != 0:
        if RuleId in handle_list_last:
            # print(CheckResult, RuleId)
            dataworks_rule_handle.objects.filter(ruleid=RuleId, over_time=over_time).update(finish_status=2)  # 更新状态为已失败
    else:
        if RuleId in handle_list_last:
            # print(CheckResult, RuleId)
            dataworks_rule_handle.objects.filter(ruleid=RuleId, over_time=over_time).update(finish_status=1)  # 更新状态为已完成


def result_conduct(table_result, handle_list, new_df, handle_list_last, tables, table_id, new_list):
    if len(table_result) != 0:
        rule_result_list = []
        for i in table_result:
            rule_result = {}
            RuleName = i.get('RuleName')
            CheckResult = i.get('CheckResult')
            EndTime = i.get('EndTime')
            BizDate = i.get('BizDate')
            RuleId = i.get('RuleId')
            try:
                error_num = i['SampleValue'][0]['Value']
            except:
                error_num = ''
            bizdate = str(datetime.datetime.fromtimestamp(int(str(BizDate)[0:-3])))
            rule_result['rulename'] = RuleName
            rule_result['checkresult'] = CheckResult
            rule_result['runtime'] = str(datetime.datetime.fromtimestamp(int(str(EndTime)[0:-3])))
            # rule_result['rundate'] = str(datetime.datetime.fromtimestamp(int(str(EndTime)[0:-3])))[0:10]
            rule_result['bizdate'] = bizdate
            rule_result['ruleid'] = RuleId
            try:
                rule_result['check_type'] = check_type_fuzzy_match(RuleName)
            except:
                continue
            rule_result['error_num'] = error_num
            result_dict = rule_handle(CheckResult, RuleId, handle_list, new_df)
            rule_result['handle_status'] = result_dict['handle_status']
            rule_result['overtime'] = result_dict['overtime']
            rule_result_list.append(rule_result)
        rule_result_list = str(rule_result_list).replace("'", '"')
        pd.set_option('display.expand_frame_repr', False)
        df = pd.read_json(rule_result_list, orient='records')
        # print(df)
        max_endtime = df.sort_values('runtime', ascending=False).groupby('ruleid', as_index=False).first()
        for index, row in max_endtime.iterrows():
            CheckResult = row.to_dict()['checkresult']
            RuleId = row.to_dict()['ruleid']
            bizdate = row.to_dict()['bizdate']
            rule_handle_status(CheckResult, RuleId, handle_list_last, bizdate[0:10])
            new_tables = tables.copy()
            new_tables.update(row.to_dict())
            new_list.append(new_tables)
    else:
        CheckResult = 3  # 规则未执行
        bizdate = tables.get('bizdate')
        result_dict = rule_handle(CheckResult, table_id, handle_list, new_df)
        rule_handle_status(CheckResult, table_id, handle_list_last, bizdate)
        tables['handle_status'] = result_dict['handle_status']
        tables['overtime'] = result_dict['overtime']
        tables['checkresult'] = 3
        tables['description'] = '规则未执行'
        new_list.append(tables)
    return new_list


class Result_Num:
    def __init__(self):
        pass

    @staticmethod
    def main(
            tables, start_date, end_date, handle_list, new_df, handle_list_last,api
    ) -> None:
        # handle_list, new_df = rule_handle_list()  # 获取当天已处理的规则id列表
        new_list = []
        table_id = tables.get('table_id')
        conn_status = True
        max_retries_count = 5  # 最大请求次数
        con_retries_count = 0  # 初始化请求次数
        # client = Result_Num.create_client('LTAI4GHKZBiC7EPpCjuN1kNU', 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL')
        while conn_status and con_retries_count <= max_retries_count:
            try:
                table_result = api.ListQualityResultsByEntity(table_id, start_date, end_date, tables)
                conn_status = False
                new_list = result_conduct(table_result, handle_list, new_df, handle_list_last, tables, table_id,
                                          new_list)
                return new_list
            except Exception as f:
                print(table_id, f)
                con_retries_count += 1
                if con_retries_count == max_retries_count:
                    CheckResult = 4
                    bizdate = tables.get('bizdate')
                    result_dict = rule_handle(CheckResult, table_id, handle_list, new_df)
                    rule_handle_status(CheckResult, table_id, handle_list_last, bizdate[0:10])
                    tables['handle_status'] = result_dict['handle_status']
                    tables['overtime'] = result_dict['overtime']
                    tables['status'] = 1
                    tables['checkresult'] = CheckResult
                    tables['description'] = 'ListQualityResultsByEntity报错'
                    new_list.append(tables)
                    return new_list
                else:
                    continue


# if __name__ == '__main__':
#     tables = {'table_id': '1537657','table_schema':'nczbigdata'}
#     start_date = '2021-07-12 00:00:00'
#     end_date = '2021-07-12 00:00:00'
#     Result_Num.main(tables, start_date, end_date)
