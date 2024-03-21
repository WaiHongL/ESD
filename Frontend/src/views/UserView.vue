<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Game from "../components/home/Game.vue";
import axios from "axios";
import { onMounted, ref } from "vue";

// DISPLAY CUSTOMIZATION MODAL WHEN CLICKED
const isCustomizationModelVisible = ref(false);
function displayCustomizationModal(bool) {
    isCustomizationModelVisible.value = bool;
}

// DISPLAY SELECTED CUSTOMIZATION
const selectedTier = ref(null);
const selectedBorderColor = ref(null);

// HANDLE CUSTOMIZATION CHANGE
function handleCustomizationChange(customization) {
    const tier = customization.tier;
    const borderColor = customization.border_color;

    selectedTier.value = tier;
    selectedBorderColor.value = borderColor;

    displayCustomizationModal(false);
}

// GET WISHLIST AND PURCHASES
const wishlist = ref([]);
let wishlistData;
const purchases = ref([]);
let purchaseData;

async function getWishlistAndPurchases() {
    await axios.get("http://localhost:5101/users/1/wishlist-and-purchases")
        .then(res => {
            const data = res.data.data;
            wishlistData = data.wishlist;
            purchaseData = data.purchases;
        })
        .catch(err => {
            console.log(err);
        });

    if (wishlistData != undefined) {
        for (const wishlistId of wishlistData) {
            const gameId = wishlistId.game_id;
            await getGameById(gameId, "wishlist");
        }
    }

    if (purchaseData != undefined) {
        for (const purchaseId of purchaseData) {
            const gameId = purchaseId.game_id;
            await getGameById(gameId, "purchases");
        }
    }
}

async function getGameById(gameId, type) {
    axios.get("http://localhost:5000/games/" + gameId)
        .then(res => {
            const data = res.data.data
            type == "wishlist" ? wishlist.value.push(data) : purchases.value.push(data);
        })
        .catch(err => {
            console.log(err);
        })
}

// GET USER POINTS
const userName = ref(null);
const points = ref(null);
const selectedCustomizationId = ref(null);
async function getUserDetails() {
    axios.get("http://localhost:5101/users/1")
        .then(res => {
            const data = res.data.data;
            userName.value = data
            points.value = data.points;
            selectedCustomizationId.value = data.selected_customization_id;
        })
        .catch(err => {
            console.log(err);
        })
}

// GET USER CUSTOMIZATIONS
const customizations = ref([]);
let customizationData;
async function getUserCustomizations() {
    await axios.get("http://localhost:5101/users/1/customizations")
        .then(res => {
            customizationData = res.data.data;
        })
        .catch(err => {
            console.log(err);
        })

    if (customizationData != undefined) {
        for (const customization of customizationData) {
            const id = customization.customization_id
            await axios.get("http://localhost:5000/customizations/" + id)
                .then(res => {
                    customizations.value.push(res.data.data);

                    if (id == selectedCustomizationId.value) {
                        selectedTier.value = res.data.data.tier;
                        selectedBorderColor.value = res.data.data.border_color;
                    }
                })
                .catch(err => {
                    console.log(err);
                })
        }
    }
}

onMounted(async () => {
    await getWishlistAndPurchases();
    await getUserDetails();
    await getUserCustomizations();
})
</script>

<template>
    <Header></Header>

    <main>
        <div class="user-container">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1>Hi Chason!</h1>
                    <div>
                        <span class="me-3"><b>Tier:</b> {{ selectedTier }}</span>
                        <span><b>Points:</b> {{ points }}</span>
                    </div>
                </div>

                <img @click="displayCustomizationModal(true)" class="user-img" :class="'border-' + selectedBorderColor"
                    src="../assets/images/user/user.jpg" />
            </div>
        </div>

        <!-- CUSTOMIZATION MODAL -->
        <div v-if="isCustomizationModelVisible" class="customization-modal-container">
            <div class="d-flex justify-content-between align-items-center">
                <div class="customization-modal-container__title">Choose your customization</div>
                <span @click="displayCustomizationModal(false)"
                    class="material-symbols-outlined customization-modal-container__close-btn">close</span>
            </div>

            <div class="d-flex justify-content-center gap-3">
                <div v-for="(customization, index) in customizations" :key="index"
                    class="customization-modal-container__customization-container">
                    <div class="customization-modal-container__border" :class="'border-' + customization.border_color">
                        {{ customization.tier }}</div>
                    <button @click="handleCustomizationChange(customization)"
                        class="btn btn-primary">Select</button>
                </div>
            </div>
        </div>

        <div v-if="isCustomizationModelVisible" class="customization-modal-container__bg"></div>

        <br /><br />

        <!-- WISHLIST -->
        <div class="wishlist-container">
            <div class="fs-4 fw-bold mb-3">My Wishlist</div>

            <div class="wishlist-container__games-container">
                <Game v-for="(game, index) in wishlist" :key="index" :title="game.title" :genre="game.genre"
                    :price="game.price" />
            </div>
        </div>

        <!-- PURCHASE -->
        <div class="purchase-container">
            <div class="fs-4 fw-bold mb-3">My Purchases</div>

            <div class="purchase-container__games-container">
                <Game v-for="(game, index) in purchases" :key="index" :title="game.title" :genre="game.genre"
                    :price="game.price" />
            </div>
        </div>
    </main>

    <Footer></Footer>
</template>

<style scoped>
main {
    width: 90%;
    max-width: 1500px;
    margin: 0 auto;
}

.user-container {
    padding-top: 50px;
    position: relative;
}

h1 {
    font-weight: 700;
    font-size: 28px;
}

.user-img {
    width: 100px;
    border-style: solid;
    border-width: 5px;
    border-radius: 50%;
    padding: 20px;
    cursor: pointer;
}

.customization-modal-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    height: 600px;
    width: 800px;
    z-index: 3;
    border-radius: 10px;
    background-color: white;
    color: black;
    padding: 50px;
}

.customization-modal-container__title {
    font-weight: 700;
    font-size: 20px;
}

.customization-modal-container__close-btn {
    cursor: pointer;
}

.customization-modal-container__customization-container {
    width: 150px;
    margin-top: 120px;
    text-align: center;
}

.customization-modal-container__border {
    height: 120px;
    border-width: 5px;
    border-style: solid;
    border-radius: 5px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
}

.customization-modal-container__btn-container {
    text-align: center;
    padding: 20px;
}

.customization-modal-container__btn-container>button {
    font-size: 14px;
}

.customization-modal-container__bg {
    position: absolute;
    inset: 0;
    background-color: black;
    opacity: 0.5;
    content: "";
    z-index: 2;
}

.wishlist-container {
    margin-bottom: 50px;
}

.wishlist-container__games-container,
.purchase-container__games-container {
    display: flex;
    gap: 75px;
}

.purchase-container {
    margin-bottom: 100px;
}
</style>
