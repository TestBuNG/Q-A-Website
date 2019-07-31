#!/usr/bin/python3
# -*- coding: utf-8 -*-
from test_plus import TestCase
from zanhu.qa.models import Question, Answer

#每次执行一个测试用例def，测试数据库就会清空
class QaModelsTest(TestCase):
    def setUp(self):
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        self.question_one = Question.objects.create(
            user=self.other_user,
            title="问题1",
            content="问题1的内容",
            tags="测试1， 测试2"
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title="问题2",
            content="问题2的内容",
            tags="测试2",
            has_answer=True
        )
        self.answer1 = Answer.objects.create(
            user=self.other_user,
            question=self.question_two,
            content="问题2的正确回答",
            is_answer=True,
        )

        self.answer2 = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content="问题2的回答",
        )

        #print("ansewr1创建时间："+str(self.answer1.created_at))
        #print("ansewr2创建时间："+str(self.answer2.created_at))

    def test_vote_question(self):
        """给问题投票"""
        self.question_one.votes.update_or_create(user=self.user, defaults={'value':True})
        self.question_one.votes.update_or_create(user=self.other_user, defaults={'value':True})
        assert self.question_one.total_votes() == 2

    def test_vote_answer_new(self):
        """给最新回答投票"""
        self.answer2.votes.update_or_create(user=self.user, defaults={'value':True})
        self.answer2.votes.update_or_create(user=self.other_user, defaults={'value':False})
        assert self.answer2.total_votes() == 0

    def test_vote_answer_old(self):
        """给不是最新的回答投票"""
        self.answer1.votes.update_or_create(user=self.user, defaults={'value':True})
        self.answer1.votes.update_or_create(user=self.other_user, defaults={'value':True})
        assert self.answer1.total_votes() == 2

    def test_get_question_voters(self):
        """获取问题投票用户"""
        self.question_one.votes.update_or_create(user=self.user, defaults={'value': True})
        self.question_one.votes.update_or_create(user=self.other_user, defaults={'value': False})
        assert self.user in self.question_one.get_upvoters()
        assert self.other_user in self.question_one.get_downvoters()

    def test_get_answer_voters(self):
        """获取回答投票用户"""
        self.answer1.votes.update_or_create(user=self.user, defaults={'value': True})
        self.answer1.votes.update_or_create(user=self.other_user, defaults={'value': False})
        assert self.user in self.answer1.get_upvoters()
        assert self.other_user in self.answer1.get_downvoters()

    def test_unanswered_question(self):
        """未回答问题"""
        assert self.question_one == Question.objects.get_unanswered()[0]

    def test_answered_question(self):
        """采纳回答的问题"""
        assert self.question_two == Question.objects.get_answered()[0]

    def test_question_get_aswers(self):
        """获取问题的所有回答"""
        assert self.answer2 == self.question_two.get_answers()[1]
        assert self.question_two.count_answers() == 2

    def test_question_accepted_answer(self):
        """提问者接受回答"""
        answer_one = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="回答1"
        )
        answer_two = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="回答2"
        )
        answer_three = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="回答3"
        )
        self.assertFalse(answer_one.is_answer)
        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)
        self.assertFalse(self.question_one.has_answer)

        # 接受 回答1 为正确答案
        answer_one.accept_answer()

        self.assertTrue(answer_one.is_answer)
        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)
        self.assertTrue(self.question_one.has_answer)

    def test_question_str_(self):
        assert isinstance(self.question_one, Question)
        assert str(self.question_one) == "问题1"

    def test_answer_str_(self):
        assert isinstance(self.answer1, Answer)
        assert str(self.answer1) == "问题2的正确回答"


