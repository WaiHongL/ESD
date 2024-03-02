<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Tier from "../components/customizations/Tier.vue";
import { ref } from "vue";

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
</script>

<template>
  <Header :key="cartKey" :cart="cart" :isAddToCartOverlayVisible="isAddToCartOverlayVisible"></Header>

  <main>
    <h1>Customizations</h1>

    <!-- Tiers -->
    <div class="tiers-container">
      <div class="tiers-container__title">Tiers</div>
      <div class="d-flex justify-content-between">
        <Tier @add-to-cart="addToCart" tier="Novice" color="Yellow" price="100"></Tier>
        <Tier @add-to-cart="addToCart" tier="Amateur" color="Green" price="200"></Tier>
        <Tier @add-to-cart="addToCart" tier="Master" color="Blue" price="300"></Tier>
        <Tier @add-to-cart="addToCart" tier="Expert" color="Red" price="400"></Tier>
        <Tier @add-to-cart="addToCart" tier="Legend" color="Black" price="500"></Tier>
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
