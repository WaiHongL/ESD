<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import { ref } from "vue";
</script>

<!-- src/views/Checkout.vue -->
<template>
    <div>
       <h1>Checkout</h1>
       <!-- Simple form for testing -->
       <form @submit.prevent="submitCheckout">
         <input type="text" v-model="name" placeholder="Name">
         <input type="email" v-model="email" placeholder="Email">
         <button type="submit">Submit</button>
       </form>
    </div>
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
        // Call your backend API to process the checkout
    }
    }
   };
   </script>