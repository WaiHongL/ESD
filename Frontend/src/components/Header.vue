<script setup>
import { ref } from "vue";

// DISPLAY CART WHEN CLICKED
const isCartVisible = ref(false);
function displayCart(bool) {
  isCartVisible.value = bool;
}

const props = defineProps({
  cart: Array,
});

console.log(props.cart);
</script>

<template>
  <header class="header-container">
    <div class="header-container__content">
      <div class="header-container__nav-container">
        <a class="header-container__site" href="./">LUDEN</a>
        <a class="header-container__nav-item" href="./customizations">Customizations</a>
      </div>

      <div class="header-container__user-container">
        <span @click="displayCart(true)" class="material-symbols-outlined me-3 header-container__cart"
          >shopping_bag</span
        >
        <div style="cursor: pointer">Chason</div>

        <div v-if="isCartVisible" class="header-container__cart-items-container">
          <div class="d-flex justify-content-between align-items-center">
            <div class="header-container__cart-items-title">My Cart</div>
            <span @click="displayCart(false)" class="material-symbols-outlined header-container__close-btn">close</span>
          </div>

          <hr />

          <!-- POPULATE CART ITEMS -->
          <div v-for="item in cart">
            <div v-if="item.title" class="d-flex justify-content-between mb-2">
              <div>
                <div class="cart-item-title">{{ item.title }}</div>
                <div class="cart-item-developer text-muted">{{ item.developer }}</div>
              </div>
              <div class="cart-item-title">${{ item.price }}</div>
            </div>
            <div v-else class="d-flex justify-content-between mb-2">
              <div class="cart-item-title">{{ item.tier }}</div>
              <div class="cart-item-title">{{ item.price }} credits</div>
            </div>
          </div>

          <button class="btn btn-primary checkout-btn">Checkout</button>
        </div>

        <div v-if="isCartVisible" class="header-container__cart-items-container-overlay"></div>
      </div>
    </div>
  </header>
</template>

<style scoped>
a {
  text-decoration: none;
  color: white;
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

.header-container__cart {
  cursor: pointer;
}

.header-container__cart-items-container {
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

.header-container__cart-items-title {
  font-weight: 700;
  font-size: 20px;
}

.header-container__close-btn {
  cursor: pointer;
}

.cart-item-title {
  font-size: 18px;
  font-weight: 700;
}

.cart-item-developer {
  font-size: 14px;
}

.checkout-btn {
  position: absolute;
  bottom: 20px;
  left: 42%;
}

.header-container__cart-items-container-overlay {
  position: fixed;
  inset: 0;
  content: "";
  background-color: black;
  opacity: 0.5;
  z-index: 2;
}
</style>
