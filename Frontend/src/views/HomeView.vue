<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Game from "../components/home/Game.vue";
import { ref } from "vue";

const cart = ref([]);
// FORCE HEADER TO RE-RENDER
const cartKey = ref(0);
function addToCart(gameData) {
  cart.value.push(gameData);
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
    <div class="background-container">
      <div class="background-container__content">
        <div class="background-container__title">
          Welcome to
          <div class="background-container__site">LUDEN</div>
        </div>
      </div>
      <div class="background-container__overlay"></div>
    </div>

    <!-- RECOMMENDATIONS -->
    <div class="recommendations-container">
      <div class="recommendations-container__title">Recommendations</div>
      <div class="recommendations-container__games-container">
        <Game @add-to-cart="addToCart" title="Palworld" developer="Pocketpair" price="26.00"></Game>
        <Game @add-to-cart="addToCart" title="DAVE THE DIVER" developer="MINTROCKET" price="21.99"></Game>
        <Game @add-to-cart="addToCart" title="Elden Ring" developer="FromSoftware" price="79.90"></Game>
      </div>
    </div>

    <!-- ALL AVAILABLE GAMES -->
    <div class="all-games-container">
      <div class="all-games-container__title">All Games</div>
      <div class="all-games-container__games-container">
        <Game @add-to-cart="addToCart" title="Palworld" developer="Pocketpair" price="26.00"></Game>
        <Game @add-to-cart="addToCart" title="DAVE THE DIVER" developer="MINTROCKET" price="21.99"></Game>
        <Game @add-to-cart="addToCart" title="Elden Ring" developer="FromSoftware" price="79.90"></Game>
      </div>
    </div>
  </main>

  <Footer></Footer>
</template>

<style scoped>
.background-container {
  background-image: url("../assets/images/home/home_background.jpg");
  width: 100%;
  height: 500px;
  background-position: top;
  background-repeat: no-repeat;
  background-size: cover;
  position: relative;
}

.background-container__overlay {
  position: absolute;
  inset: 0;
  background-color: black;
  opacity: 0.5;
  content: "";
}

.background-container__content {
  width: 90%;
  height: 100%;
  max-width: 1500px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
}

.background-container__title {
  color: white;
  font-size: 40px;
  font-weight: 200;
}

.background-container__site {
  font-size: 50px;
  font-weight: 700;
  letter-spacing: 4px;
}

.recommendations-container,
.all-games-container {
  width: 90%;
  max-width: 1500px;
  margin: 0 auto;
  padding: 50px 0;
  font-family: "Poppins";
}

.all-games-container {
  margin-bottom: 50px;
}

.recommendations-container__title,
.all-games-container__title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 20px;
}

.recommendations-container__games-container,
.all-games-container__games-container {
  display: flex;
  justify-content: space-between;
}
</style>
