<script setup>
import { ref } from "vue";

const props = defineProps({
  wishlist: Array,
  isAddToWishlistOverlayVisible: Boolean,
});

// DISPLAY WISHLIST WHEN CLICKED
const isWishlistVisible = ref(false);
function displayWishlist(bool) {
  isWishlistVisible.value = bool;
}
</script>

<template>
  <header class="header-container">
    <div class="header-container__content">
      <div class="header-container__nav-container">
        <a class="header-container__site" href="./">LUDEN</a>
        <a class="header-container__nav-item" href="./customizations">Customizations</a>
      </div>

      <div class="header-container__user-container">
        <span
          @click="displayWishlist(true)"
          class="material-symbols-outlined me-3 header-container__wishlist"
          :class="{ 'text-primary': wishlist && wishlist.length >= 1 }"
          >shopping_bag</span>
        <a href="./user">Chason</a>

        <div v-if="isWishlistVisible" class="header-container__wishlist-items-container">
          <div class="d-flex justify-content-between align-items-center">
            <div class="header-container__wishlist-items-title">My Wishlist</div>
            <span @click="displayWishlist(false)" class="material-symbols-outlined header-container__close-btn">close</span>
          </div>

          <hr />

          <!-- POPULATE WISHLIST ITEMS -->
          <div v-for="item in wishlist">
            <div v-if="item.title" class="d-flex justify-content-between mb-2">
              <div>
                <div class="wishlist-item-title">{{ item.title }}</div>
                <div class="wishlist-item-developer text-muted">{{ item.genre }}</div>
              </div>
              <div class="wishlist-item-title">${{ item.price }}</div>
            </div>
            <div v-else class="d-flex justify-content-between mb-2">
              <div class="wishlist-item-title">{{ item.tier }}</div>
              <div class="wishlist-item-title">{{ item.price }} credits</div>
            </div>
          </div>

          <button class="btn btn-primary checkout-btn" :class="{ disabled: wishlist && wishlist.length == 0 }">Checkout</button>
        </div>

        <div v-if="isWishlistVisible" class="header-container__wishlist-items-container-overlay"></div>
      </div>
    </div>

    <!-- ADD TO WISHLIST OVERLAY -->
    <div v-if="isAddToWishlistOverlayVisible" class="add-to-wishlist-overlay">Item has been added to wishlist.</div>
  </header>
</template>

<style scoped>
a {
  text-decoration: none;
  color: white;
  cursor: pointer;
}

.header-container {
  height: 70px;
  background-color: black;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
}

.header-container__content {
  width: 90%;
  max-width: 1500px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-container__nav-container {
  display: flex;
}

.header-container__site {
  font-weight: 700;
  letter-spacing: 2px;
  margin-right: 20px;
}

.header-container__user-container {
  display: flex;
  justify-content: center;
}

.header-container__wishlist {
  cursor: pointer;
}

.header-container__wishlist-items-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  height: 600px;
  width: 600px;
  z-index: 3;
  border-radius: 10px;
  background-color: white;
  color: black;
  padding: 20px 30px;
}

.header-container__wishlist-items-title {
  font-weight: 700;
  font-size: 20px;
}

.header-container__close-btn {
  cursor: pointer;
}

.wishlist-item-title {
  font-size: 18px;
  font-weight: 700;
}

.wishlist-item-developer {
  font-size: 14px;
}

.checkout-btn {
  position: absolute;
  bottom: 20px;
  left: 42%;
}

.header-container__wishlist-items-container-overlay {
  position: fixed;
  inset: 0;
  content: "";
  background-color: black;
  opacity: 0.5;
  z-index: 2;
}

.add-to-wishlist-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  width: 400px;
  height: 200px;
  background-color: white;
  color: black;
  border-radius: 10px;
  border: 3px solid black;
  display: flex;
  justify-content: center;
  align-items: center;
}

.add-to-wishlist-overlay-opacity {
}
</style>
