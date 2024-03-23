<script setup>
import axios from "axios";
import { computed, ref } from "vue";

const props = defineProps({
    id: Number,
    title: String,
    genre: String,
    price: Number,
    isWishlist: Boolean,
    isWishlistDisabled: Boolean,
    isPurchaseDisabled: Boolean,
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

console.log(props.title + " isWishlist: " + props.isWishlist);
console.log(props.title + " isWishlistDisabled: " + props.isWishlistDisabled);
console.log(props.title + " isPurchaseDisabled: " + props.isPurchaseDisabled);
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

                <div class="d-flex">
                    <button @click="$emit('handleWishlist',{ id, isWishlist})" class="btn py-2 me-2 border-0" :class="{ 'btn-success': isWishlist, 'btn-danger': !isWishlist }" :disabled="isWishlistDisabled">
                        <span class="material-symbols-outlined text-white d-flex align-items-center">favorite</span>
                    </button>

                    <!-- <button @click="$emit('addToCart', { title, genre, price })" class="btn bg-primary py-2 border-0"
                        :disabled="disabled">
                        <span class="material-symbols-outlined text-white d-flex align-items-center">shopping_bag</span>
                    </button> -->
                    <button class="btn bg-primary py-2 border-0" :disabled="isPurchaseDisabled">
                        <span class="material-symbols-outlined text-white d-flex align-items-center">shopping_bag</span>
                    </button>
                </div>
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
