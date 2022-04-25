def sql1(phone):
    """
    查找手机号
    :param phone:
    :return:
    """
    sql = '''SELECT member_id FROM user_info WHERE member_phone='{}';'''.format(phone)
    return sql


def sql2(member_id):
    """
    删除t_member中的这个用户
    :param member_id:
    :return:
    """
    sql = '''DELETE FROM user_info WHERE member_id={};'''.format(member_id)
    return sql


def sql3(member_id):
    """
    删除t_member_star中的这个用户
    :param member_id:
    :return:
    """
    sql = '''DELETE FROM user_shop_level_tree WHERE member_id={};'''.format(member_id)
    return sql


def sql4(member_id):
    """
    删除t_member_base_ext中的这个用户
    :param member_id:
    :return:
    """
    sql = '''DELETE FROM user_base_ext WHERE member_id={};'''.format(member_id)
    return sql


def sql5(member_id):
    """
    删除t_member中的这个用户
    :param member_id:
    :return:
    """
    sql = '''DELETE FROM user_mother_bean WHERE member_id={};'''.format(member_id)
    return sql
