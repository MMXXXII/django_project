<script setup>
import {ref} from 'vue';

const a =  ref();
const b = ref();
const c = ref(0)

async function onLoadClick() {

}

</script>

<template>
<div>
    <div v-for="item in list" class = "library-item">
        <b>{{item.fio}}</b> <b></b>
        
    </div>
</div>
</template>

<style scoped>

</style>
