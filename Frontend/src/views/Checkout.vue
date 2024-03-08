<!-- if need -->

<script setup>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import { ref } from "vue";
import { Stripe, loadStripe, StripePlugin } from '@vue-stripe/vue-stripe';
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
 <!-- Add a container for the Stripe Elements card input -->
 <div id="card-element"></div>
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
        <button @click="submitCheckout()" class="btn btn-primary btn-lg btn-block">Pay now</button>
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
        nameOnCard: '',
        cvv: '',
        expiryDate: ''
      };
    },
    async mounted() {
    // Initialize Stripe
    const stripe = await loadStripe('pk_test_51LrjcfK1WW7DRh3qozq21D4vjLWPEPCEvUlElldx7B3kxJ0KlScZzZS8B17tNBs2cNJLCm83hNMx3HDgVXagGGOM00IYhIPgw7');
    const elements = stripe.elements();
    const cardElement = elements.create('card');
    cardElement.mount('#card-element');

    // Store the cardElement in the component's data for later use
    this.cardElement = cardElement;
  },
    methods: {
      async submitCheckout() {
      const stripe = Stripe('pk_test_51LrjcfK1WW7DRh3qozq21D4vjLWPEPCEvUlElldx7B3kxJ0KlScZzZS8B17tNBs2cNJLCm83hNMx3HDgVXagGGOM00IYhIPgw7');
      const {clientSecret} = await fetch('/create-payment-intent', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ totalprice: 99.99 }) // Adjust the total price as needed
      }).then(response => response.json());

      
      
      const result = await stripe.confirmCardPayment(
        clientSecret,{
          payment_method:{
            card:cardElement,
            billing_details: {
              name: this.nameOnCard
            }
          }
        }
      );
      if (result.error) {
        console.error(result.error.message);
        // Handle payment failure
      } else {
        // Handle payment success
        console.log('Payment successful');
      }
      }
    }
       
  }
</script>