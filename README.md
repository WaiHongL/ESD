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
### API Key: (Replace with your Publishable key)
```bash
pk_test_51LrjcfK1WW7DRh3qozq21D4vjLWPEPCEvUlElldx7B3kxJ0KlScZzZS8B17tNBs2cNJLCm83hNMx3HDgVXagGGOM00IYhIPgw7
```

### Locate API Key:
1. Login to your Stripe account
2. Select "Test mode"
3. Replace API Key with your Publishable Key

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