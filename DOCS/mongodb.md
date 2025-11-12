# DOCS/mongodb.md

GET /mongodb/images/{file_id}                    # Thumbnail по ID
GET /mongodb/images/thumb/{file_id}              # Thumbnail по ID (альтернатива)
GET /mongodb/files/{filename}                    # Thumbnail по имени файла  
GET /mongodb/files/thumb/{filename}              # Thumbnail по имени файла (альтернатива)

GET /mongodb/images/full/{file_id}               # Полное изображение по ID
GET /mongodb/images/{file_id}?full=true          # Полное изображение по ID (с параметром)
GET /mongodb/files/full/{filename}               # Полное изображение по имени файла
GET /mongodb/files/{filename}?full=true          # Полное изображение по имени (с параметром)

<!-- Список изображений - показываем thumbnails -->
<div class="image-grid">
  <div v-for="image in images" :key="image.id">
    <img :src="`/mongodb/images/${image.id}`" 
         @click="showFullImage(image.id)"
         class="thumbnail">
  </div>
</div>

<!-- Модальное окно с полным изображением -->
<modal v-if="selectedImage">
  <img :src="`/mongodb/images/full/${selectedImage.id}`" 
       class="full-image">
</modal>




! ЕСЛИ ПРИ ПЕРВОМ ЗАПУСКЕ ЗАВИСАЕТ (НЕ МОЖЕТ СОЗДАТЬ ПОЛЬЗОВАТЕЛЯ)
1. закомментировать эту строку (бывает что пытается сосздать полльзователя повторно и все рушит)
   1. - ./mongo/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
2. СОЗДАТЬ ВРУЧНУЮ
docker-compose exec mongo mongo
use admin
db.createUser({
  user: "admin",
  pwd: "admin",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" },
    { role: "dbAdminAnyDatabase", db: "admin" }
  ]
})
exit
ВОЙТИ ПОД ЛОГИНОМ СОЗДАННОГО ПОЛЬЗОВАТЕЛЯ И ОБНОВИТЬ ПРАВА

docker-compose exec mongo mongo -u admin -p admin --authenticationDatabase admin
use admin
db.updateUser(
  "admin",
  {
    roles: [
      { role: "dbAdminAnyDatabase", db: "admin" },
      { role: "readWriteAnyDatabase", db: "admin" },
      { role: "userAdminAnyDatabase", db: "admin" },
      { role: "clusterAdmin", db: "admin" }  // Добавь это для доступа к config
    ]
  }
)

exit