<script setup>
import { onMounted, ref } from 'vue';
import { loadStripe } from '@stripe/stripe-js';
import axios from 'axios';
import { useRoute } from 'vue-router';
import router from '@/router';

// GET GAME ID
const route = useRoute();
const gameId = route.params.gameId;
const gameTitle = ref(null);
const gameGenre = ref(null);
const gamePrice = ref(null);

function getGameDetails() {
    axios.get("http://localhost:5000/games/" + gameId)
        .then((res) => {
            const data = res.data.data;
            gameTitle.value = data.title;
            gameGenre.value = data.genre;
            gamePrice.value = data.price;
        })
        .catch((err) => {
            console.log(err);
        });
}

// CREATE STRIPE CARD
const stripePromise = ref(null);
const cardElement = ref(null);
async function createCardElement() {
    loadStripe('pk_test_51LrjcfK1WW7DRh3qozq21D4vjLWPEPCEvUlElldx7B3kxJ0KlScZzZS8B17tNBs2cNJLCm83hNMx3HDgVXagGGOM00IYhIPgw7')
        .then(res => {
            stripePromise.value = res;
            const elements = stripePromise.value.elements();

            // Create a Card Element
            cardElement.value = elements.create("card");

            // Mount the Card Element to a DOM element
            cardElement.value.mount("#card-element");
        })
        .catch(err => {
            console.log(err);
        });
}

// HANDLE SUBMIT
const isPaymentProcessing = ref(false);
const isPaymentUnsuccessful = ref(false);
function handleSubmit() {
    stripePromise.value.createPaymentMethod({
        type: "card",
        card: cardElement.value,
    })
        .then(async (res) => {
            // HANDLE INVALID CARD NUMBER
            if (res.error) {
                console.log(res.error.message);
            } else {
                const axiosData = {
                    "purchase_id": res.paymentMethod.id,
                    "user_id": "1", // TO BE CHANGED
                    "game_id": gameId,
                }

                isPaymentProcessing.value = true;

                await axios.post("http://localhost:5100/make-purchase", axiosData)
                    .then(res => {
                        if (res.data.code == 200) {
                            router.push("/");
                            isPaymentProcessing.value = false;
                        } else {
                            isPaymentUnsuccessful.value = true;
                            setTimeout(() => {
                                isPaymentUnsuccessful.value = false;
                                isPaymentProcessing.value = false;
                            }, 5000);
                        }
                    })
                    .catch(err => {
                        console.log(err);
                        isPaymentUnsuccessful.value = true;
                        setTimeout(() => {
                            isPaymentUnsuccessful.value = false;
                            isPaymentProcessing.value = false;
                        }, 5000);
                    })
            }
        })
        .catch(err => {
            console.log(err);
        })
}

onMounted(async () => {
    getGameDetails();
    await createCardElement();
})
</script>

<template>
    <div class="d-flex">
        <div class="item-container">
            <div class="item-container__content">
                <h1 class="item-container__site mb-4">LUDEN</h1>

                <div class="mb-3">
                    <div>{{ gameTitle }}</div>
                    <div class="text-muted">{{ gameGenre }}</div>
                </div>

                <div class="item-container__price">${{ gamePrice }}</div>
            </div>

            <img class="item-container__img" src="../assets/images/checkout/gaming.jpg">
        </div>

        <div class="payment-container">
            <div class="payment-container__content">
                <h2 class="payment-container__title">Purchase Information</h2>

                <label for="email" class="w-100 mb-3">
                    <div class="mb-2">Email</div>
                    <input type="text" id="email" class="form-control">
                </label>

                <div class="mb-2">Shipping Address</div>
                <label for="name" class="w-100 mb-2">
                    <input type="text" id="name" class="form-control" placeholder="Name">
                </label>

                <label for="address" class="w-100 mb-3">
                    <input type="text" id="address" class="form-control" placeholder="Address">
                </label>

                <div class="mb-2">Card Information</div>
                <div class="mb-5" id="card-element"></div>

                <button class="btn btn-primary w-100" @click="handleSubmit()">Pay</button>
            </div>
        </div>
    </div>

    <div v-if="isPaymentProcessing" class="payment-processing-bg"></div>
    <div v-if="isPaymentProcessing && isPaymentUnsuccessful" class="payment-processing-modal">Payment unsuccessful
    </div>
    <div v-else-if="isPaymentProcessing && !isPaymentUnsuccessful" class="payment-processing-modal">Payment processing...
    </div>
</template>

<style scoped>
.item-container {
    width: 50%;
    height: 100vh;
    border-right: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
    position: relative;
}

.item-container__content {
    width: 400px;
    margin: 0 auto;
    padding-top: 60px;
}

.item-container__site {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
}

.item-container__price {
    font-weight: 700;
    font-size: 32px;
}

.item-container__img {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 400px;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: 5px;
}

.payment-container {
    width: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.payment-container__content {
    width: 70%;
    max-width: 450px;
}

.payment-container__title {
    font-weight: 700;
    font-size: 20px;
    margin-bottom: 20px;
}

input {
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

.payment-processing-bg {
    position: fixed;
    inset: 0;
    content: "";
    background-color: black;
    opacity: 0.5;
}

.payment-processing-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 300px;
    height: 150px;
    z-index: 2;
    background-color: white;
    border-radius: 10px;
    border: 3px solid black;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>