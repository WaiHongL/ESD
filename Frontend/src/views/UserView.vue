<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
</script>

<template>
  <Header></Header>

  <main>
    <h1>Hi Chason!</h1>
    <br><br>
    <img class="user-img border-warning" src="../assets/images/user/user.jpg" alt="">
    <br><br>
    <div class="tier"><b>Tier:</b> Novice</div>
  </main>

  <Footer></Footer>
</template>

<style scoped>
main {
  height: calc(100vh - 70px - 90px);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

h1 {
    font-weight: 700;
    font-size: 28px;
    text-align: center;
}

.user-img {
    width: 300px;
    margin: 0 auto;
    border-style: solid;
    border-width: 10px;
    border-radius: 50%;
    padding: 20px;
}

.tier {
    text-align: center;
    font-size: 20px;
}
</style>
