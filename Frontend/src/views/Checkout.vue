<!-- if need -->

<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import { ref } from "vue";
</script>

<template>
  <Header :key="cartKey" :cart="cart" :isAddToCartOverlayVisible="isAddToCartOverlayVisible"></Header>

    <div>
      <h1>Checkout</h1>
      <!-- form for testing -->
      <form @submit.prevent="submitCheckout">
        <input type="text" v-model="name" placeholder="Name">
        <input type="email" v-model="email" placeholder="Email">
        <button type="submit">Submit</button>
      </form>
    </div>
  <Footer></Footer>
</template>
   
<script>
  export default {
    data() {
      return {
        name: '',
        email: ''
      };
    },
    methods: {
      submitCheckout() {
        //
      }
    }       
  };
</script>