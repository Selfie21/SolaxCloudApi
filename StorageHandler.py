class StorageHandler:

    def add_name(userID, name):
        try:
            response = table.put_item(
                Item={
                    'UserID': userID,
                    'Name': name
                }
            )
        except ClientError as e:
            print(e.response)
            return e.response['Error']['Code']

        return Nonedef
        delete_name(userID, name):
        try:
            response = table.delete_item(
                Key={
                    'UserID': userID,
                    'Name': name
                }
            )
        except ClientError as e:
            print(e.response)
            return e.response['Error']['Code']
            return None