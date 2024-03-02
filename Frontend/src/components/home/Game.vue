<script setup>
import { computed } from "vue";

const props = defineProps({
  title: String,
  genre: String,
  price: Number,
});

// GET IMAGE SOURCE
const imgSrc = computed(() => {
  let src = "/src/assets/images/home/";
  if (props.title === "DAVE THE DIVER") {
    src += "dave_the_diver.jpg";
  } else if (props.title === "Elden Ring") {
    src += "elden_ring.jpg";
  } else {
    src += "palworld.jpg";
  }
  return src;
});
</script>

<template>
  <div class="card">
    <img :src="imgSrc" class="card-img-top" />
    <div class="card-body">
      <h5 class="card-title">{{ title }}</h5>
      <div class="card-subtitle text-muted">{{ genre }}</div>
      <br />
      <div class="d-flex justify-content-between align-items-center">
        <div class="card-price">${{ price }}</div>
        <button @click="$emit('addToWishlist', { title, genre, price })" class="btn bg-primary text-white">
          Add to Wishlist
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  width: 30%;
}

.card-body {
  padding: 20px 30px;
}

.card-img-top {
  aspect-ratio: 1.5 / 1;
  object-fit: cover;
}

.card-title {
  font-weight: bold;
  font-size: 24px;
  margin-bottom: 5px;
}

.card-subtitle {
  font-size: 18px;
}

.card-price {
  font-size: 20px;
}
</style>
