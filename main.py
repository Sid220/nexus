import requests
from basecampapi.basecampapi import Basecamp
from basecampapi.basecampapi import MessageBoard


class BCManager:
    # credentials = {
    #     "account_id": "5855125",
    #     "client_id": "1b53154c47ecb8e11e9a44c527a8abca14cea1fa",
    #     "client_secret": "5e8e7245114032ddb000de2029216bc6e48bc31d",
    #     "redirect_uri": "https://b621-50-170-108-90.ngrok-free.app/auth",
    #     "refresh_token": "BAhbB0kiAbB7ImNsaWVudF9pZCI6IjFiNTMxNTRjNDdlY2I4ZTExZTlhNDRjNTI3YThhYmNhMTRjZWExZmEiLCJleHBpcmVzX2F0IjoiMjAzNC0xMS0wNFQxMzo0NTozOFoiLCJ1c2VyX2lkcyI6WzUwMTMwMzE4XSwidmVyc2lvbiI6MSwiYXBpX2RlYWRib2x0IjoiZWU1N2E5YjNjNDdjMzNmMGQ4YmIzN2JkOWE5NDQzMmEifQY6BkVUSXU6CVRpbWUNjaghwAMwZLYJOg1uYW5vX251bWkCVQE6DW5hbm9fZGVuaQY6DXN1Ym1pY3JvIgc0EDoJem9uZUkiCFVUQwY7AEY=--0efd4326320a9acc4c29925929a2371515d96414"
    # }

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
