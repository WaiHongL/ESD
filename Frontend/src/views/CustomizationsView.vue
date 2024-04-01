<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Tier from "../components/customizations/Tier.vue";
import { onMounted, ref } from "vue";
import axios from "axios";

// const cart = ref([]);
// // FORCE HEADER TO RE-RENDER
// const cartKey = ref(0);
// function addToCart(customizationData) {
//     cart.value.push(customizationData);
//     displayAddToCartOverlay();
//     cartKey.value += 1;
// }

// // DISPLAY ADD TO CART CONFIRMATION
// const isAddToCartOverlayVisible = ref(false);
// function displayAddToCartOverlay() {
//     isAddToCartOverlayVisible.value = true;
//     setTimeout(() => {
//         isAddToCartOverlayVisible.value = false;
//     }, 2000);
// }

// Purchase customization
const isPurchaseModalDisplayed = ref(false);
const isPurchaseUnsuccessful = ref(false);
async function handlePurchase(customizationData) {
    const userPoints = await getUserPoints()

    if (userPoints < customizationData.points) {
        isPurchaseModalDisplayed.value = true;
        isPurchaseUnsuccessful.value = true;

        setTimeout(() => {
            isPurchaseModalDisplayed.value = false;
        }, 3000);
    } else {
        isPurchaseModalDisplayed.value = true;
        try {
            createPurchaseRecord(customizationData.id);
            updateUserPoints(customizationData.points);

            setTimeout(() => {
                isPurchaseModalDisplayed.value = false;
                window.location.reload();
            }, 3000);
        } catch (error) {
            console.log(error)
            isPurchaseUnsuccessful.value = true;

            setTimeout(() => {
                isPurchaseModalDisplayed.value = false;
            }, 3000);
        }
    }
}

async function getUserPoints() {
    let userPoints;
    await axios.get("http://localhost:5600/users/1")
        .then(res => {
            const data = res.data.data;
            userPoints = data.points;
        })
        .catch(err => {
            console.log(err);
        });

    return userPoints;
}

function createPurchaseRecord(customizationId) {
    const axiosData = {
        "user_id": 1,
        "customization_id": customizationId
    }

    axios.post("http://localhost:5600/users/customization-purchase/create", axiosData)
        .then(res => {})
        .catch(err => {
            console.log(err);
        });
}

function updateUserPoints(customizationPoints) {
    const axiosData = {
        "user_id": 1,
        "price": customizationPoints / 100,
        "operation": "subtract"
    }

    axios.put("http://localhost:5600/users/points/update", axiosData)
        .then(res => {})
        .catch(err => {
            console.log(err);
        })
}

// GET ALL AVAILABLE CUSTOMIZATIONS
const customizations = ref([])
function getAllCustomizations() {
    axios.get("http://localhost:5601/shop/customizations")
        .then((res) => {
            customizations.value = res.data.data.customizations;
        })
        .catch((err) => {
            console.log(err);
        });
}

// GET USER CUSTOMIZATIONS
const purchases = ref([]);
let purchaseData;
async function getPurchases() {
    await axios.get("http://localhost:5600/users/1/customizations")
        .then(res => {
            const data = res.data.data;
            purchaseData = data;
        })
        .catch(err => {
            console.log(err);
        });

    if (purchaseData != undefined) {
        for (const purchaseId of purchaseData) {
            const customizationId = purchaseId.customization_id;
            purchases.value.push(customizationId);
        }
    }
}

onMounted(async () => {
    await getPurchases();
    getAllCustomizations();
})
</script>

<template>
    <Header :key="cartKey" :cart="cart" :isAddToCartOverlayVisible="isAddToCartOverlayVisible"></Header>

    <main>
        <h1>Customizations</h1>

        <!-- Tiers -->
        <div class="tiers-container">
            <div class="tiers-container__title">Tiers</div>
            <div class="d-flex justify-content-between">
                <!-- <Tier v-for="(customization, index) in customizations" :key="index" @add-to-cart="addToCart"
                    :tier="customization.tier" :borderColor="customization.border_color" :points="customization.points"></Tier> -->
                <Tier v-for="(customization, index) in customizations" :key="index" @handle-purchase="handlePurchase"
                    :id="customization.customization_id" :tier="customization.tier"
                    :borderColor="customization.border_color" :points="customization.points"
                    :disabled="purchases.includes(customization.customization_id)"></Tier>
            </div>
        </div>
    </main>

    <div v-if="isPurchaseModalDisplayed" class="purchase-modal-bg"></div>
    <div v-if="isPurchaseUnsuccessful && isPurchaseModalDisplayed" class="purchase-modal">
        Purchase unsuccessful
    </div>
    <div v-else-if="!isPurchaseUnsuccessful && isPurchaseModalDisplayed" class="purchase-modal">Purchase
        successful
    </div>

    <Footer></Footer>
</template>

<style scoped>
main {
    height: calc(100vh - 70px - 90px);
    display: flex;
    flex-direction: column;
    justify-content: center;
}

h1 {
    text-align: center;
    font-weight: bold;
    font-size: 28px;
    padding-bottom: 50px;
}

.tiers-container {
    width: 90%;
    max-width: 1500px;
    margin: 0 auto;
}

.tiers-container__title {
    font-weight: 700;
    font-size: 24px;
    margin-bottom: 10px;
}

.purchase-modal-bg {
    position: fixed;
    inset: 0;
    content: "";
    background-color: black;
    opacity: 0.5;
}

.purchase-modal {
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
