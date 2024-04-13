import base64
import json
import unittest
from unittest import mock

from cloudevents.http import CloudEvent

from main import PubSource, handle_message_from_list_generator, handle_message_from_bot
from mock_list import mock_orders

mock_data = {
    "message": "lalala",
    "source": PubSource.LIST_GENERATOR,
    "chat_id": "aa1234"
}

mock_data_from_bot = {
    "message": "lalala",
    "chat_id": "aa1234"
}

mock_data_bytes = bytes(json.dumps(mock_data), 'utf-8')

attributes = {
    "type": "XXX",
    "source": "XXX",
}
c = CloudEvent(data={"message": {"data": base64.b64encode(mock_data_bytes)}}, attributes=attributes)


class TestInvoke(unittest.TestCase):
    @mock.patch('main.get_list')
    @mock.patch('rag.RagPrompt._chain_invoke')
    @mock.patch('rag.RagPrompt._get_llm')
    def test_handle_message_from_list_generator(self, mock_get_llm, chain_invoke, mock_get_data):
        mock_get_llm.return_value = dict()
        mock_get_data.return_value = mock_orders
        chain_invoke.return_value = "list_text"
        message, history = handle_message_from_list_generator(mock_data)
        expected_history_contains = "תכין לי רשימת קניות"
        self.assertEqual(history[0][0], "human")
        self.assertIn(expected_history_contains, history[0][1])
        self.assertEqual(history[1], ("ai", "list_text"))
        self.assertEqual(message, "#from_llm#list_text")

    @mock.patch('main.get_history')
    @mock.patch('main.get_list')
    @mock.patch('rag.RagPrompt._chain_invoke')
    @mock.patch('rag.RagPrompt._get_llm')
    def test_handle_message_from_bot_after_list(self, mock_get_llm, chain_invoke, mock_get_list, mock_get_history):
        mock_get_llm.return_value = dict()
        chain_invoke.return_value = "generic_text"
        mock_get_list.return_value = mock_orders
        mock_get_history.return_value = '[]'
        message, history = handle_message_from_bot(mock_data_from_bot)
        expected_history = [("human", "lalala"), ("ai", "generic_text")]
        self.assertEqual(expected_history, history)
        self.assertEqual(message, "#from_llm#generic_text")

    @mock.patch('main.get_history')
    @mock.patch('main.get_list')
    @mock.patch('rag.RagPrompt._chain_invoke')
    @mock.patch('rag.RagPrompt._get_llm')
    def test_handle_message_from_bot_before_list(self, mock_get_llm, chain_invoke, mock_get_list, mock_get_history):
        mock_get_llm.return_value = dict()
        chain_invoke.return_value = "generic_text"
        mock_get_list.return_value = '[]'
        mock_get_history.return_value = '[]'
        message, history = handle_message_from_bot(mock_data_from_bot)
        expected_history = [("human", "lalala"), ("ai", "generic_text")]
        self.assertEqual(len(history), 4)
        self.assertEqual(history[2:], expected_history)
        self.assertEqual(message, "#from_llm#generic_text")
