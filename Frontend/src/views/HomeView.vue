<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Game from "../components/home/Game.vue";
import { onMounted, ref } from "vue";
import axios from "axios";

const cart = ref([]);
// FORCE HEADER TO RE-RENDER
const cartKey = ref(0);
function addToCart(gameData) {
	cart.value.push(gameData);
	displayAddToCartOverlay();
	cartKey.value += 1;
}

// DISPLAY ADD TO CART CONFIRMATION
const isAddToCartOverlayVisible = ref(false);
function displayAddToCartOverlay() {
	isAddToCartOverlayVisible.value = true;
	setTimeout(() => {
		isAddToCartOverlayVisible.value = false;
	}, 2000);
}

// GET ALL AVAILABLE GAMES
const games = ref([]);
function getAllGames() {
	axios.get("http://localhost:5000/games")
		.then((res) => {
			games.value = res.data.data.games;
		})
		.catch((err) => {
			console.log(err);
		});
}

// GET RECOMMENDED GAMES
const recommendedGames = ref([]);
function getRecommendedGames() {
	axios.get("http://localhost:5500/recommendations/1")
		.then((res) => {
			recommendedGames.value = res.data.data.games;
		})
		.catch((err) => {
			console.log(err);
		});
}

onMounted(() => {
	getAllGames();
	getRecommendedGames();
});
</script>

<template>
	<Header :key="cartKey" :cart="cart" :isAddToCartOverlayVisible="isAddToCartOverlayVisible"></Header>

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
				<Game v-if="recommendedGames.length" v-for="(game, index) in recommendedGames" :key="index"
					@add-to-cart="addToCart" :title="game.title" :genre="game.genre" :price="game.price" />
				<div v-else class="fs-5 text-muted">Loading recommendations...</div>
			</div>
		</div>

		<!-- ALL AVAILABLE GAMES -->
		<div class="all-games-container">
			<div class="all-games-container__title">All Games</div>
			<div class="all-games-container__games-container">
				<Game v-for="(game, index) in games" :key="index" @add-to-cart="addToCart" :title="game.title"
					:genre="game.genre" :price="game.price" />
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
	gap: 75px;
}

.all-games-container__games-container {
	flex-wrap: wrap;
}
</style>
