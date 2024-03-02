<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Tier from "../components/customizations/Tier.vue";
import { ref } from "vue";

const wishlist = ref([]);
// FORCE HEADER TO RE-RENDER
const wishlistKey = ref(0);
function addToWishlist(customizationData) {
  wishlist.value.push(customizationData);
  displayAddToWishlistOverlay();
  wishlistKey.value += 1;
}

// DISPLAY ADD TO WISHLIST CONFIRMATION
const isAddToWishlistOverlayVisible = ref(false);
function displayAddToWishlistOverlay() {
  isAddToWishlistOverlayVisible.value = true;
  setTimeout(() => {
    isAddToWishlistOverlayVisible.value = false;
  }, 2000);
}
</script>

<template>
  <Header :key="wishlistKey" :wishlist="wishlist" :isAddToWishlistOverlayVisible="isAddToWishlistOverlayVisible"></Header>

  <main>
    <h1>Customizations</h1>

    <!-- Tiers -->
    <div class="tiers-container">
      <div class="tiers-container__title">Tiers</div>
      <div class="d-flex justify-content-between">
        <Tier @add-to-wishlist="addToWishlist" tier="Novice" color="Yellow" price="100"></Tier>
        <Tier @add-to-wishlist="addToWishlist" tier="Amateur" color="Green" price="200"></Tier>
        <Tier @add-to-wishlist="addToWishlist" tier="Master" color="Blue" price="300"></Tier>
        <Tier @add-to-wishlist="addToWishlist" tier="Expert" color="Red" price="400"></Tier>
        <Tier @add-to-wishlist="addToWishlist" tier="Legend" color="Black" price="500"></Tier>
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
