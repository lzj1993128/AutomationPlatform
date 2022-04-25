class ReportUtil:
    def report(self, title, totalNum, passNum, failNum, errorNum, trList):
        """
        html报告模板
        :param title: 标题
        :param totalNum: 用例总数
        :param passNum: 用例通过数
        :param failNum: 用例跳过数
        :param errorNum: 用例错误数
        :param trList: 每行的用例结果
        :return:
        """
        report = '''
                <!DOCTYPE html>
                 <html>
                 <head>
                 <title>自动化测试报告</title>
                 <style type="text/css">
                 table{
                    width: 600px;
                    text-align:left;
                    font-size:11px;
                    border-color: #666666;
                    border-collapse: collapse;
                    }
                 th {
                     border-width: 1px;
                     padding: 8px;border-style: 
                     solid;border-color: #666666;
                     background-color: #dedede;
                     }
                 td {
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #666666;
                    background-color: #ffffff;
                 }
                 h1 {
                     font-size: 16pt;
                     color: gray;
                 }
                 .heading {
                     margin-top: 0ex;
                     margin-bottom: 1ex;
                 }
                 .heading .attribute {
                     margin-top: 1ex;
                     margin-bottom: 0;
                 }
                 .heading .description {
                     margin-top: 4ex;
                     margin-bottom: 6ex;
                 }
                 </style>
                 </head>
                 <body>
                 <!-- 头部 -->
                 <div class='heading'>
                 <h1> ''' + title + '''</h1>
                 </div>
                 <p class="attribute">
                 <h2 style=" color: gray;"><strong>执行情况:</strong></h2><br>
                 <span style="font-size: 18px">Count:''' + totalNum + '''</span><br>
                 <span style="color: #16E8BF;font-size: 18px">Pass:''' + passNum + '''</span><br>
                 <span style="color: #F96D85;font-size: 18px">Fail:''' + failNum + '''</span><br>
                 <span style="color: #F5B913;font-size: 18px">Error:''' + errorNum + '''</span><br>
                 </p>
                 <p class="description">用例执行情况如下：</p>
                 <!-- 表格 -->
                 <table>
                 <tr>
                 <th>用例ID</th>
                 <th>用例名称</th>
                 <th>执行结果</th>
                 </tr>
                 ''' + trList + '''
                 </table>
                 </body>
                 </html>'''
        return report

    def trList(self, caseId=None, case_name=None, result=None):
        """
        每行的数据组装
        :return:
        """
        tr = "<tr>" + "<td>" + str(caseId) + "</td>" + "<td>" + str(case_name) + "</td>" + "<td>" + str(
            result) + "</td>" + "</tr>"
        return tr
