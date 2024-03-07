<!-- if need -->

<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import { ref } from "vue";
</script>

<template>
  <Header :key="cartKey" :cart="cart" :isAddToCartOverlayVisible="isAddToCartOverlayVisible"></Header>

  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <!-- Product Details Segment -->
        <div class="card mb-3">
          <div class="row no-gutters">
            <div class="col-md-4">
              <img src="https://source.unsplash.com/JrZvYuBYzCU" class="card-img" alt="Game Image">
            </div>
            <div class="col-md-8">
              <div class="card-body">
                <h5 class="card-title">Test-Game-Name</h5>
                <p class="card-text">$99.99</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Payment Details Segment -->
        <form @submit.prevent="submitCheckout" class="mb-3">
          <div class="form-group">
            <label for="nameOnCard">Name on Card</label>
            <input type="text" class="form-control" id="nameOnCard" v-model="nameOnCard">
          </div>
          <div class="form-group">
            <label for="cardNumber">Card Number</label>
            <input type="text" class="form-control" id="cardNumber" v-model="cardNumber">
          </div>
          <div class="form-group">
            <label for="cvv">CVV</label>
            <input type="text" class="form-control" id="cvv" v-model="cvv">
          </div>
          <div class="form-group">
            <label for="expiryDate">Expiry Date</label>
            <input type="text" class="form-control" id="expiryDate" v-model="expiryDate">
          </div>
          <!-- Add more fields as needed -->
        </form>

        <!-- Pay Button -->
        <button @click="submitCheckout()" type="submit" class="btn btn-primary btn-lg btn-block">Pay now</button>
      </div>
    </div>
  </div>

  <Footer></Footer>
  <!-- anyone can help why the footer here need fixed-bottom the others dont need -->
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
        console.log("hello")
      }
    }       
  };
</script>