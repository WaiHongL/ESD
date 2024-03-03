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
  } else if (props.title === "Palworld") {
    src += "palworld.jpg";
  } else if (props.title == "Oxygen Not Included") {
    src += "oxygen_not_included.jpg";
  }
  return src;
});
</script>

<template>
  <div class="card mb-4">
    <div class="row g-0">
      <div class="col-md-5">
        <img :src="imgSrc" class="img-fluid rounded-start" />
      </div>

      <div class="col-md-7">
        <div class="card-body">
          <div class="text-start">
            <h5 class="card-title">{{ title }}</h5>
            <div class="card-text text-muted">{{ genre }}</div>
          </div>

          <div class="d-flex justify-content-between align-items-center">
            <div class="card-price">${{ price }}</div>
            <button class="btn bg-primary justify-content-center align-items-center">
              <span class="material-symbols-outlined d-flex justify-content-center align-items-center text-white">shopping_bag</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  max-width: 550px;
}

img {
  aspect-ratio: 1.5 / 1;
  object-fit: cover;
}

.card-body {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
}

.card-price {
    font-size: 18px;
}

.btn {
    padding: 5px 8px;
}

.material-symbols-outlined {
    font-size: 22px;
}
</style>
