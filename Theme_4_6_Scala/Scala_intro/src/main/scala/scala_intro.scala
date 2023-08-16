object HelloWorld {
  def main(args: Array[String]) = {
    val message = "Hello, Scala!"
    // Выводим фразу на печать
    println(message)

    // Выводим фразу справа налево, используя метод reverse
    println(message.reverse)

    // Переводим всю фразу в нижний регистр, используя метод toLowerCase
    val lowerCaseMessage = message.toLowerCase

    // Удаляем символ !, используя метод replace
    val modifiedMessage = lowerCaseMessage.replace("!", "")

    // Добавляем в конец фразы, используя метод concat
    val finalMessage = modifiedMessage.concat(" and goodbye python!")

    // Выводим итоговую фразу на экран
    println(finalMessage)
  }
}
