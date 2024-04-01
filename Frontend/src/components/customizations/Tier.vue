<script setup>
import { computed, ref } from "vue";
import axios from "axios";

const props = defineProps({
    id: Number,
    tier: String,
    borderColor: String,
    points: Number,
    disabled: Boolean,
});

const borderColor = computed(() => {
    return "border-" + props.borderColor;
});
</script>

<template>
    <div class="card">
        <div class="card-border" :class="borderColor">
            <div class="card-tier">{{ tier }}</div>
        </div>

        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div class="card-title">{{ tier }}</div>
                <div class="card-price">{{ points }} points</div>
            </div>

            <div class="text-center">
                <!-- <button @click="$emit('addToCart', { tier, price })" class="btn btn-primary" :disabled="disabled">Add to Cart</button> -->
                <button class="btn btn-primary" :disabled="disabled" @click="$emit('handlePurchase', { id, points })">Purchase</button>
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
