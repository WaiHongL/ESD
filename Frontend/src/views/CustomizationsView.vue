<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Tier from "../components/customizations/Tier.vue";
import { onMounted, ref } from "vue";
import axios from "axios";

const cart = ref([]);
// FORCE HEADER TO RE-RENDER
const cartKey = ref(0);
function addToCart(customizationData) {
    cart.value.push(customizationData);
    displayAddToCartOverlay();
    cartKey.value += 1;
}

// DISPLAY ADD TO CART CONFIRMATION
const isAddToCartOverlayVisible = ref(false);
function displayAddToCartOverlay() {
    isAddToCartOverlayVisible.value = true;
    setTimeout(() => {
        isAddToCartOverlayVisible.value = false;
    }, 2000);
}

// GET ALL AVAILABLE CUSTOMIZATIONS
const customizations = ref([])
function getAllCustomizations() {
    axios.get("http://localhost:5000/customizations")
        .then((res) => {
            customizations.value = res.data.data.customizations;
            console.log(customizations.value);
        })
        .catch((err) => {
            console.log(err);
        });
}

onMounted(() => {
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
                <!-- <Tier @add-to-cart="addToCart" tier="Novice" color="Yellow" price="500"></Tier>
                <Tier @add-to-cart="addToCart" tier="Amateur" color="Green" price="1000"></Tier>
                <Tier @add-to-cart="addToCart" tier="Master" color="Blue" price="2000"></Tier>
                <Tier @add-to-cart="addToCart" tier="Expert" color="Red" price="4000"></Tier>
                <Tier @add-to-cart="addToCart" tier="Legend" color="Black" price="8000"></Tier> -->
                <Tier v-for="(customization, index) in customizations" :key="index" @add-to-cart="addToCart"
                    :tier="customization.tier" :credits="customization.credits"></Tier>
            </div>
        </div>
    </main>

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
</style>
