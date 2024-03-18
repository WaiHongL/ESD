<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import Game from "../components/home/Game.vue";
</script>

<template>
    <Header></Header>

    <main>
        <div class="user-container">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1>Hi Chason!</h1>
                    <div>
                        <span class="me-3"><b>Tier:</b> Novice</span>
                        <span><b>Points:</b> 500</span>
                    </div>
                </div>

                <img class="user-img" src="../assets/images/user/user.jpg" />
            </div>
        </div>

        <br /><br />

        <!-- WISHLIST -->
        <div class="wishlist-container">
            <div class="fs-4 fw-bold mb-3">My Wishlist</div>

            <div class="wishlist-container__games-container">
                <Game title="Palworld" genre="Open World" price="26.00"></Game>
                <Game title="Elden Ring" genre="Open World" price="79.90"></Game>
            </div>
        </div>

        <!-- PURCHASE -->
        <div class="purchase-container">
            <div class="fs-4 fw-bold mb-3">My Purchases</div>

            <div class="purchase-container__games-container">
                <Game @add-to-cart="addToCart" title="DAVE THE DIVER" genre="Simulation" price="21.99"></Game>
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
    width: 120px;
    /* border-style: solid;
    border-width: 10px;
    border-radius: 50%; */
    padding: 20px;
}

.wishlist-container {
    margin-bottom: 50px;
}

.wishlist-container__games-container,
.purchase-container__games-container {
    display: flex;
    gap: 20px;
}

.purchase-container {
    margin-bottom: 100px;
}
</style>
