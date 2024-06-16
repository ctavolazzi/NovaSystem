import sys
import json
import pocketbase

def update_pocketbase(messages):
    pb = pocketbase.PocketBase('http://127.0.0.1:8090')

    admin_email = 'ctavolazzi@gmail.com'
    admin_password = 'adminpassword'

    try:
        # Authenticate the admin account
        auth_data = pb.admins.auth_with_password(admin_email, admin_password)

        if auth_data:
            admin_token = auth_data.token
            print(f"Admin authenticated successfully. Token: {admin_token}")

            # Prepare the data to be sent to the crewai_runs collection
            data = {
                "json": json.dumps({"messages": messages}),
                "description": "Updated messages from the AI chat"
            }

            try:
                # Update the record in the crewai_runs collection
                response = pb.collection('ai_chats').update('ic74gxca6sa97sp', data)

                if response:
                    print("Record updated successfully:")
                    print(f"ID: {response.id}")
                    print(f"JSON: {response.json}")
                    print(f"Description: {response.description}")
                else:
                    print("Failed to update record.")
            except Exception as e:
                print(f"Error updating record: {str(e)}")

            # Clear the auth store to log out the admin account
            pb.auth_store.clear()
        else:
            print("Failed to authenticate admin.")
    except Exception as e:
        print(f"Error: {str(e)}")

# Read messages from stdin
input_data = sys.stdin.read()

# Parse the input data as JSON
data = json.loads(input_data)
messages = data['messages']

# Update PocketBase
update_pocketbase(messages)