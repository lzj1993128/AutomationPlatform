from datetime import datetime
import json

from api.models import Robot, User
from common.base.BaseService import BaseService


class RobotService(BaseService):
    def saveRebot(self, requestData, userId):
        """
        保存机器人
        :return:
        """
        group_name = requestData['group_name']
        robotList = requestData['robotList']
        username = User.objects.get(user_id=userId).username
        robot = Robot(group_name=group_name, type=1, creator=username, update_person=username)
        robot.save()
        robot_id = robot.robot_id
        for robots in robotList:
            robot_name = robots['robot_name']
            web_hook = robots['web_hook']
            keywordList = json.dumps(robots['keywordList'])
            Robot(group_name=group_name, p_id=robot_id, type=2, robot_name=robot_name, web_hook=web_hook,
                  keywordList=keywordList,
                  creator=username, update_person=username).save()

    def editRobot(self, requestData, userId):
        """
        编辑机器人
        :return:
        """
        robot_id = requestData['robot_id']
        group_name = requestData['group_name']
        robotList = requestData['robotList']
        username = User.objects.get(user_id=userId).username
        Robot.objects.filter(robot_id=robot_id).update(group_name=group_name, update_person=username,
                                                       update_time=datetime.now())
        for robots in robotList:
            robot_ids = robots['robot_id'] if 'robot_id' in robots.keys() else None
            robot_name = robots['robot_name']
            web_hook = robots['web_hook']
            keywordList = json.dumps(robots['keywordList'])
            if robot_ids:
                Robot.objects.filter(robot_id=robot_ids).update(group_name=group_name, p_id=robot_id, type=2,
                                                                robot_name=robot_name, web_hook=web_hook,
                                                                keywordList=keywordList, update_person=username,
                                                                update_time=datetime.now())
            else:
                Robot(group_name=group_name, p_id=robot_id, type=2, robot_name=robot_name, web_hook=web_hook,
                      keywordList=keywordList,
                      creator=username, update_person=username).save()
