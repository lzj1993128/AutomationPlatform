def countBigData(filds, report_id):
    """
    通过report_id,查询出本次的结果
    :param filds:传入某个字段进行统计
    :param report_id:
    :return:
    """
    sql = '''
    select sum({})
    from big_data_bigdatahistory
    where report = {:d}
    '''.format(filds, report_id)
    return sql