from mailjet_rest import Client
from flask import Flask, redirect, request

app = Flask(__name__, static_url_path="", static_folder="public")


api_key = "d2d21f40f8f6cd7b51784638c46b078b"
api_secret = "7c5652e91572a9fb541b985737e0371a"


@app.route("/notification")
def send_email():
    mailjet = Client(auth=(api_key, api_secret), version="v3.1")
    data = {
        "Messages": [
            {
                "From": {
                    "Email": "caijun.ng.2021@economics.smu.edu.sg",
                    "Name": "Cai Jun",
                },
                "To": [
                    {"Email": "zhijie.neo.2022@scis.smu.edu.sg", "Name": "Neo Zji Jie"},
                    {
                        "Email": "weifeng.koh.2022@scis.smu.edu.sg",
                        "Name": "Koh Wei Feng",
                    },
                    {"Email": "whliew.2022@scis.smu.edu.sg", "Name": "Liew Wai Hong"},
                    {"Email": "jernic.yeo.2022@scis.smu.edu.sg", "Name": "Jernic Yeo"},
                    {"Email": "shida.tan.2022@scis.smu.edu.sg", "Name": "Tan Shi Da"},
                ],
                "Cc": [
                    {
                        "Email": "caijun.ng.2021@economics.smu.edu.sg",
                        "Name": "Ng Cai Jun",
                    }
                ],
                "Subject": "Greetings from Mailjet.",
                "TextPart": "My first Mailjet email",
                "HTMLPart": "ZHI JIE IS GAY",
                "CustomID": "AppGettingStartedTest",
            }
        ]
    }
    result = mailjet.send.create(data=data)
    # return (result.status_code)
    return result.json()


if __name__ == "__main__":
    app.run(port=5200, debug=True)
