# Luden
Luden is an online game store that aims to provide users with a seamless and engaging experience, offering a diverse range of games and personalised recommendations tailored to their preferences. Leveraging a microservice architecture, we have created modules such as game recommendations, purchases, and refunds. 

## Getting Started
```bash
# Step 1: Start Docker containers
cd backend
docker compose up -d

# Step 2: Run the app
cd frontend
npm run dev
```

## Stripe
### API Keys: 
```bash
# Publishable Key: (Replace with your own key)
pk_test_51LrjcfK1WW7DRh3qozq21D4vjLWPEPCEvUlElldx7B3kxJ0KlScZzZS8B17tNBs2cNJLCm83hNMx3HDgVXagGGOM00IYhIPgw7

# Secret Key: (Replace with your own key)
sk_test_51LrjcfK1WW7DRh3qSpVCT1CWMxeC8bpxPOQdTWJ6SyFCJCSpt6opHUXb1QqB65u8zvxdrmkzYqNcZy2TBHoSzjX000cRwCOEA6
```

### Locate API Key:
1. Login to your Stripe account
2. Click on Developers
3. Replace API Key with your Publishable Key
4. Click reveal test key and replace Secret Key with your Secret Key

### Test Card Numbers:
```bash
# Simulate payment success
Card number: 4242424242424242

# Simulate payment failure
Card number: 4000000000009995

MM/YY: 04/24
CVC: 4242
```

### Check Transactions Status on Stripe:
1. Login to your Stripe account
2. Navigate to Payments tab

## MailJet
API Keys:
```bash
# API Key
b234bb351a835b67c4f8ce412a8e77ab

# Secret Key
d20ed987dd240464d6f4bd92af7247de
```

### Locate API Key:
1. Login to your Mailjet account
2. Select "API"
3. Replace API and Secret Key with the API and Secret Key shown

### Check Email Status on Mailjet:
1. Login to your Mailjet account
2. In homepage, Real-time message events shows dashboard of sent email status within the past 30 minutes
3. In the same homepage, Latest messages sent shows sent email status within the past 24 hours


## Using Flasgger for API Documentation
Flasgger is a Flask extension that extracts OpenAPI-Specification from all Flask views registered in your API. It comes with a Swagger UI that allows you to visualize and interact with your API's resources without having any of the implementation logic in place.

### How to Test Flasgger Documentation
To test the Flasgger documentation for your services, follow these steps:

1. Start your Docker containers as you normally would. This can be done by navigating to your project's backend directory and running the command:
```bash
docker compose up -d
```

2. 2. Once the containers are up and running, you can access the Flasgger documentation for each of your services by navigating to the `/apidocs/` endpoint on your local machine. The URL format is as follows:
```bash
http://localhost:<portnum>/apidocs/
```

For example, if you want to view the documentation for the user service, which is running on port 5600, you would navigate to:
```bash
http://localhost:5600/apidocs/
# This will open the Swagger UI in your web browser, displaying all the available API endpoints, their parameters, and the expected responses. You can use this interface to test your API endpoints directly from your browser.
```