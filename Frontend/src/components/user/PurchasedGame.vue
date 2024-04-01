<script setup>
import { computed } from "vue";

const props = defineProps({
    id: Number,
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
    } else if (props.title == "PUBG: BATTLEGROUNDS") {
        src += "pubg_battlegrounds.jpg";
    } else if (props.title == "HELLDIVERS 2") {
        src += "helldivers_2.jpg";
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

            <div class="d-flex justify-content-end align-items-center">
                <div></div>
                <button @click="$emit('handleRefund', { id, title, genre, price })"
                    class="btn bg-primary ml-auto">
                    <span class="text-white">Refund</span>
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
