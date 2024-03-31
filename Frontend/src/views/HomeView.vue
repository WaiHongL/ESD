<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Game from "../components/home/Game.vue";
import { onMounted, ref } from "vue";
import axios from "axios";

// const cart = ref([]);
// // FORCE HEADER TO RE-RENDER
// const cartKey = ref(0);

// // HANDLE WHEN ADD TO CART BUTTON IS CLICKED
// function addToCart(gameData) {
// 	cart.value.push(gameData);
// 	displayAddToCartOverlay();
// 	cartKey.value += 1;
// }

// // DISPLAY ADD TO CART CONFIRMATION
// const isAddToCartOverlayVisible = ref(false);
// function displayAddToCartOverlay() {
// 	isAddToCartOverlayVisible.value = true;
// 	setTimeout(() => {
// 		isAddToCartOverlayVisible.value = false;
// 	}, 2000);
// }

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
	// console.log("Wishlist before: " + wishlist.value);
	await getWishlistAndPurchases();
	// console.log("Wishlist after: " + wishlist.value);
	getRecommendedGames();
}

// GET ALL AVAILABLE GAMES
const games = ref([]);
async function getAllGames() {
	await axios.get("http://localhost:5601/shop/games")
		.then((res) => {
			const data = res.data.data;
			games.value = data.games;
		})
		.catch((err) => {
			console.log(err);
		});
}

// GET RECOMMENDED GAMES
const recommendedGames = ref([]);
const isRecommendedGamesLoading = ref(false);
async function getRecommendedGames() {
	isRecommendedGamesLoading.value = true;
	recommendedGames.value = [];
	await axios.get("http://localhost:5603/create-recommendation/1")
		.then((res) => {
			const data = res.data.data;
			recommendedGames.value = data.games;
		})
		.catch((err) => {
			console.log(err);
		});
	isRecommendedGamesLoading.value = false;
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

			if (!wishlist.value.includes(gameId)) { // HANDLE ADD WISHLIST
				wishlist.value.push(gameId);
			} else if (wishlist.value.length > wishlistData.length) { // HANDLE DELETE WISHLIST
				wishlist.value = [];
				wishlist.value.push(gameId);
			}
		}
	} else { // HANDLE NO GAMES IN WISHLIST AFTER DELETION
		wishlist.value = [];
	}

	if (purchaseData != undefined) {
		for (const purchaseId of purchaseData) {
			const gameId = purchaseId.game_id;

			if (!purchases.value.includes(gameId)) {
				purchases.value.push(gameId);
			} else if (purchases.value.length > purchaseData.length) {
				purchases.value = [];
				purchases.value.push(gameId);
			}
		}
	} else {
		purchases.value = [];
	}
}

onMounted(async () => {
	await getWishlistAndPurchases();
	await getAllGames();
	getRecommendedGames();
});
</script>

<template>
	<!-- <Header :key="cartKey" :cart="cart" :isAddToCartOverlayVisible="isAddToCartOverlayVisible"></Header> -->
	<Header></Header>

	<main>
		<div class="background-container">
			<div class="background-container__content">
				<div class="background-container__title">
					Welcome to
					<div class="background-container__site">LUDEN</div>
				</div>
			</div>
			<div class="background-container__overlay"></div>
		</div>

		<!-- RECOMMENDATIONS -->
		<div class="recommendations-container">
			<div class="recommendations-container__title">Recommendations</div>
			<div class="recommendations-container__games-container"
				:class="{ 'justify-content-center': recommendedGames.length == 0 }">
				<!-- <Game v-if="recommendedGames.length" v-for="(game, index) in recommendedGames" :key="index"
					@add-to-cart="addToCart" :title="game.title" :genre="game.genre" :price="game.price" /> -->
				<!-- <Game v-if="recommendedGames.length" v-for="(game, index) in recommendedGames" :key="index"
					:id="game.game_id" :title="game.title" :genre="game.genre" :price="game.price" /> -->

				<div v-if="isRecommendedGamesLoading" class="fs-5 text-muted">Loading recommendations...</div>
				<Game v-else-if="!isRecommendedGamesLoading && recommendedGames.length"
					v-for="(game, index) in recommendedGames" :key="index" :id="game.game_id" :title="game.title"
					:genre="game.genre" :price="game.price" @handle-wishlist="handleWishlist"
					:isWishlist="wishlist.includes(game.game_id)" :isWishlistDisabled="purchases.includes(game.game_id)"
					:isPurchaseDisabled="purchases.includes(game.game_id)" />
				<div v-else class="fs-5 text-muted">No recommendations</div>

			</div>
		</div>

		<!-- ALL AVAILABLE GAMES -->
		<div class="all-games-container">
			<div class="all-games-container__title">All Games</div>
			<div class="all-games-container__games-container" :key="wishlistKey">
				<!-- <Game v-for="(game, index) in games" :key="index" @add-to-cart="addToCart" :title="game.title"
					:genre="game.genre" :price="game.price" /> -->
				<Game v-for="(game, index) in games" :key="index" :id="game.game_id" :title="game.title"
					:genre="game.genre" :price="game.price" @handle-wishlist="handleWishlist"
					:isWishlist="wishlist.includes(game.game_id)" :isWishlistDisabled="purchases.includes(game.game_id)"
					:isPurchaseDisabled="purchases.includes(game.game_id)" />
			</div>
		</div>
	</main>

	<Footer></Footer>
</template>

<style scoped>
.background-container {
	background-image: url("../assets/images/home/home_background.jpg");
	width: 100%;
	height: 500px;
	background-position: top;
	background-repeat: no-repeat;
	background-size: cover;
	position: relative;
}

.background-container__overlay {
	position: absolute;
	inset: 0;
	background-color: black;
	opacity: 0.5;
	content: "";
}

.background-container__content {
	width: 90%;
	height: 100%;
	max-width: 1500px;
	margin: 0 auto;
	position: relative;
	z-index: 2;
	display: flex;
	align-items: center;
}

.background-container__title {
	color: white;
	font-size: 40px;
	font-weight: 200;
}

.background-container__site {
	font-size: 50px;
	font-weight: 700;
	letter-spacing: 4px;
}

.recommendations-container,
.all-games-container {
	width: 90%;
	max-width: 1500px;
	margin: 0 auto;
	padding: 50px 0;
	font-family: "Poppins";
}

.all-games-container {
	margin-bottom: 50px;
}

.recommendations-container__title,
.all-games-container__title {
	font-size: 24px;
	font-weight: 700;
	margin-bottom: 20px;
}

.recommendations-container__games-container,
.all-games-container__games-container {
	display: flex;
	gap: 5%;
}

.all-games-container__games-container {
	flex-wrap: wrap;
	row-gap: 50px;
}
</style>
