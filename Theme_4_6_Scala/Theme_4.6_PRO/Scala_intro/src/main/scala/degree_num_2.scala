import scala.io.StdIn.{readInt, readLine}

object Recurcy extends App {
  def powerOfTwo(n: Int): Int = {
    if (n == 0) {
      1
    } else {
      2 * powerOfTwo(n - 1)
    }
  }

  import scala.annotation.tailrec

  def powerOfTwoTail(n: Int): Int = {
    @tailrec
    def loop(acc: Int, x: Int): Int = {
      if (x == 0) {
        acc
      } else {
        loop(2 * acc, x - 1)
      }
    }
    loop(1, n)
  }

  def userRequest(): Unit = {
    println("Введите число, для которого нужно найти 2^n:")
    val n = scala.io.StdIn.readInt()
    val result1 = powerOfTwo(n)
    val result2 = powerOfTwoTail(n)
    println(s"Результат (обычная рекурсия): 2^$n = $result1")
    println(s"Результат (хвостовая рекурсия): 2^$n = $result2")
  }

  userRequest()
}
