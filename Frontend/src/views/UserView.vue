<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Game from "../components/home/Game.vue";
import PurchasedGame from "../components/user/PurchasedGame.vue";
import axios from "axios";
import { onMounted, ref, computed } from "vue";

// HANDLE REFUND UPON CLICK OF REFUND BUTTON
const isRefundProcessing = ref(false);
const isRefundUnsuccessful = ref(false);
const isRefundModalDisplayed = ref(false);
async function handleRefund(gameData) {
    var game_Id = gameData.id
    var axiosData = {
        "user_id": "1", // TO BE CHANGED
        "game_id": game_Id,
    }
    // CALL REFUND COMPLEX MICROSERVICE HERE
    isRefundProcessing.value = true;
    await axios.post("http://localhost:5606/refund-game", axiosData)
        .then(res => {
            if (res.data.code == 200) {
                isRefundProcessing.value = false;
                isRefundModalDisplayed.value = true;
                setTimeout(() => {
                    isRefundModalDisplayed.value = false;
                    window.location.reload();
                }, 3000);
            } else {
                isRefundProcessing.value = false;
                isRefundUnsuccessful.value = true;
                isRefundModalDisplayed.value = true;
                setTimeout(() => {
                    isRefundModalDisplayed.value = false;
                    window.location.reload();
                }, 3000);
            }
        })
        .catch(err => {
            console.log(err);
            isRefundProcessing.value = false;
            isRefundUnsuccessful.value = true;
            isRefundModalDisplayed.value = true;
            setTimeout(() => {
                isRefundModalDisplayed.value = false;
                window.location.reload();
            }, 3000);
        })
}

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
    const id = customization.customization_id;
    const tier = customization.tier;
    const borderColor = customization.border_color;

    const axiosData = {
        "user_id": 1,
        "customization_id": id
    }

    axios.put("http://localhost:5600/users/customizations/update", axiosData)
        .then(res => {
            console.log(res);
        })
        .catch(err => {
            console.log(err);
        })

    selectedTier.value = tier;
    selectedBorderColor.value = borderColor;

    displayCustomizationModal(false);
}

// HANDLE WISHLIST
async function handleWishlist(data) {
    const axiosData = {
        "user_id": 1,
        "game_id": data.id
    };

    if (!data.isWishlist) {
        await axios.post("http://localhost:5600/users/wishlist/create", axiosData)
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            })
    } else {
        await axios.delete("http://localhost:5600/users/wishlist/delete", { data: axiosData })
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            })
    }
    await getWishlistAndPurchases();
}

// GET WISHLIST AND PURCHASES
const wishlist = ref([]);
let wishlistData;
const purchases = ref([]);
let purchaseData;

async function getWishlistAndPurchases() {
    await axios.get("http://localhost:5600/users/1/wishlist-and-purchases")
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

            if (purchaseData != undefined && !purchaseData.some(purchase => purchase.game_id == gameId)) {
                if (!wishlist.value.some(wish => wish.game_id == gameId)) {
                    await getGameById(gameId, "wishlist");
                } else if (wishlist.value.length > wishlistData.length) {
                    wishlist.value = [];
                    await getGameById(gameId, "wishlist");
                }
            } else if (purchaseData == undefined) {
                if (!wishlist.value.some(wish => wish.game_id == gameId)) {
                    await getGameById(gameId, "wishlist");
                } else if (wishlist.value.length > wishlistData.length) {
                    wishlist.value = [];
                    await getGameById(gameId, "wishlist");
                }
            }
        }
    } else {
        wishlist.value = [];
    }

    if (purchaseData != undefined) {
        for (const purchaseId of purchaseData) {
            const gameId = purchaseId.game_id;

            if (!purchases.value.some(purchase => purchase.game_id == gameId)) {
                await getGameById(gameId, "purchases");
            } else if (purchases.value.length > wishlistData.length) {
                purchases.value = [];
                await getGameById(gameId, "purchases");
            }
        }
    } else {
        purchases.value = [];
    }
}

async function getGameById(gameId, type) {
    axios.get("http://localhost:5601/shop/games/" + gameId)
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
    axios.get("http://localhost:5600/users/1")
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
    await axios.get("http://localhost:5600/users/1/customizations")
        .then(res => {
            customizationData = res.data.data;
        })
        .catch(err => {
            console.log(err);
        })

    if (customizationData != undefined) {
        for (const customization of customizationData) {
            const id = customization.customization_id
            await axios.get("http://localhost:5601/shop/customizations/" + id)
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

const borderColor = computed(() => {
    return "border-" + selectedBorderColor.value;
});

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
                        <span class="me-3"><b>Tier:</b> {{ selectedTier ? selectedTier : "None" }}</span>
                        <span><b>Points:</b> {{ points }}</span>
                    </div>
                </div>

                <img @click="displayCustomizationModal(true)" class="user-img" :class="borderColor"
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
                    <button @click="handleCustomizationChange(customization)" class="btn btn-primary">Select</button>
                </div>
            </div>
        </div>

        <div v-if="isCustomizationModelVisible" class="customization-modal-container__bg"></div>

        <br /><br />

        <!-- WISHLIST -->
        <div class="wishlist-container">
            <div class="fs-4 fw-bold mb-3">My Wishlist</div>

            <div v-if="wishlist.length" class="wishlist-container__games-container">
				<Game v-for="(game, index) in wishlist" :key="index" :id="game.game_id" :title="game.title"
					:genre="game.genre" :price="game.price" @handle-wishlist="handleWishlist"
					:isWishlist="true" />
            </div>

            <div class="text-center" v-else>You have no games in your wishlist</div>
        </div>

        <!-- PURCHASE -->
        <div class="purchase-container">
            <div class="fs-4 fw-bold mb-3">My Purchases</div>

            <div v-if="purchases.length" class="purchase-container__games-container">
                <PurchasedGame v-for="(game, index) in purchases" :key="index" :id="game.game_id" :title="game.title"
                    :genre="game.genre" @handle-refund="handleRefund" />
            </div>

            <div class="text-center" v-else>You have no purchases</div>
        </div>

        <!-- REFUND MODAL -->
        <div v-if="isRefundProcessing || isRefundModalDisplayed" class="refund-modal-bg"></div>
        <div v-if="!isRefundProcessing && isRefundUnsuccessful && isRefundModalDisplayed" class="refund-modal">Refund is unsuccessful
        </div>
        <div v-else-if="isRefundProcessing && !isRefundModalDisplayed" class="refund-modal">Refund is being
            processed...
        </div>
        <div v-else-if="!isRefundProcessing && !isRefundUnsuccessful && isRefundModalDisplayed"
            class="refund-modal">Refund is successful
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

.refund-modal-bg {
    position: fixed;
    inset: 0;
    content: "";
    background-color: black;
    opacity: 0.5;
}

.refund-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 300px;
    height: 150px;
    z-index: 2;
    background-color: white;
    border-radius: 10px;
    border: 3px solid black;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
