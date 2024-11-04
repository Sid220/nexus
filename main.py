import requests
from basecampapi.basecampapi import Basecamp
from basecampapi.basecampapi import MessageBoard


class BCManager:
    def __init__(self, config):
        self.bc = Basecamp(credentials=config.to_dict())

        self.msg_board = MessageBoard(config.project_id, config.msg_board_id)
        msgs = self.msg_board.get_all_messages()

        title_to_search = "[QUEUEING NOTIFICATIONS - AUTOMATIC]"

        # Search for the message with the given title
        message_found = next((m for m in msgs if m["title"] == title_to_search), None)

        if message_found:
            self.message_id = message_found["id"]
            print(f"Message found with ID: {self.message_id}")
        else:
            data = self.msg_board.create_message(title_to_search,
                                            "Queueing notifications will be published here automatically. "
                                            "Powered by FRC Nexus. <a href='https://frc.nexus'>Learn "
                                            "more...</a>")
            self.message_id = data["id"]
            self.msg_board.create_comment(self.message_id, "Queuing notifications will appear here as they are published.")
            print(f"New message created with ID: {self.message_id}")

    def post_event(self, event):
        print(f"Posting event: {event}")
        self.msg_board.create_comment(self.message_id, event)
