<!-- if need -->

<script>
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";
import { ref, onMounted } from "vue";
import { loadStripe } from '@stripe/stripe-js';

let cardElement;
const stripePromise = loadStripe('pk_test_51LrjcfK1WW7DRh3qozq21D4vjLWPEPCEvUlElldx7B3kxJ0KlScZzZS8B17tNBs2cNJLCm83hNMx3HDgVXagGGOM00IYhIPgw7');

const createCardElement = async () => {
  try {
    // Get the stripe object from stripePromise
    const stripe = await stripePromise;
    console.log(stripe)
    // Create a Card Element
    const elements = stripe.elements();
    console.log('logging elements')
    console.log(elements)
    cardElement = elements.create('card');
    console.log('logging cardelement')
    console.log(cardElement)

    // Mount the Card Element to a DOM element
    cardElement.mount('#card-element');

    // Handle validation and other events for the Card Element
    cardElement.on('change', (event) => {
      // Handle validation errors or other changes to the Card Element
      console.log(event);
    });

    // Return the Card Element
    return cardElement;
  } catch (error) {
    console.error('Error:', error+' hii');
    return null;
  }
};



export default {
    data() {
      return {
        nameOnCard: '',
        cardNumber:'',
        cvv: '',
        expiryDate: ''
      };
    },
    methods:{
async submitCheckout(){
  console.log('sdadf')
  try {
    // Get the stripe object from stripePromise
    console.log('hello')
    const stripe = await stripePromise;
    console.log(stripe)
    
    // const cardElement = await createCardElement();
    console.log('submit')
    console.log((cardElement))

    // Use Stripe.js to create a payment intent and handle payment confirmation
    const paymentMethod  = stripe.createPaymentMethod({
    type: 'card',
    card: cardElement,
    
  }).then(async function(result) {
    console.log('logging res')
    console.log(result)
    console.log('done')
    console.log(result.paymentMethod.id)

    const response = await fetch('http://localhost:5100/make-purchase', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ paymentmethod_id: result.paymentMethod.id,
        "user_id": "3",
        "game_id": "2"
       }),
    });
    const data = await response.json();
    console.log(data);


//     const { paymentIntent, error } = await stripe.confirmCardPayment(data.client_secret, {
//   payment_method: {
//     card: cardElement,
//     billing_details: {
//       name: 'Jenny Rosen',
//     },
//   }
// });

if (data['code'] == 400) {
  console.error('Error:', data['code']);
  // Handle payment failure
  const response = await fetch('http://localhost:5100/payment-fail', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ paymentMethodid: result.paymentMethod.id,
        "user_id": "3",
        "game_id": "2"
       }),
    });

} else {
  console.log('Payment successful');
  //show payment success modal??
}
  });
  
  

    

    // Send payment intent ID to backend
    

    // Handle response from backend as needed
    
    
  } catch (error) {
    console.log('sian')
    console.error('Error:', error);
  }
}
    },
    mounted() {
    createCardElement();
  }}
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
        <form class="mb-3">
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
        <button v-on:click="submitCheckout" class="btn btn-primary btn-lg btn-block">Pay now</button>
      </div>
    </div>
  </div>

  <Footer></Footer>
  <!-- anyone can help why the footer here need fixed-bottom the others dont need -->
</template>
   
