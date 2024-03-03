<script setup>
import { computed } from "vue";

const props = defineProps({
  tier: String,
  color: String,
  price: Number,
});

const borderColor = computed(() => {
  let bootstrapColor = "black";
  if (props.color == "Yellow") {
    bootstrapColor = "warning";
  } else if (props.color == "Green") {
    bootstrapColor = "success";
  } else if (props.color == "Blue") {
    bootstrapColor = "primary";
  } else if (props.color == "Red") {
    bootstrapColor = "danger";
  }
  return "border-" + bootstrapColor;
});
</script>

<template>
  <div class="card">
    <div class="card-border" :class="borderColor">
      <div class="card-tier">{{ tier }}</div>
    </div>

    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="card-title">{{ tier }}</h5>
        <div class="card-price">{{ price }} credits</div>
      </div>
      
      <div class="text-center">
        <button @click="$emit('addToCart', { tier, price })" class="btn btn-primary">Add to Cart</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  width: 18%;
}

.card-border {
  aspect-ratio: 1.5 / 1;
  border-style: solid;
  border-width: 5px;
  border-radius: 5px 5px 0 0;
  position: relative;
}

.card-tier {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.card-title {
  font-size: 18px;
  font-weight: 700;
}

.btn {
  font-size: 14px;
}
</style>
