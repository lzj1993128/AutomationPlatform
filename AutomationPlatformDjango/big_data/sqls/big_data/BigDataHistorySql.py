def bigDataHistorySql(big_data_id_list):
    """
    查询sql
    :param big_data_id_list:
    :return:
    """
    big_data_id_list = ','.join('%s' %id for id in big_data_id_list)
    sql = '''
    SELECT *
    FROM big_data_bigdatahistory
    WHERE big_data_id IN ({})
    ORDER BY create_time DESC
    '''.format(big_data_id_list)
    return sql
