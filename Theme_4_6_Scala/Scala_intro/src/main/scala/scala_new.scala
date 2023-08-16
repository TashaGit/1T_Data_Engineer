import scala.io.StdIn.{readDouble}


object Main {
  def main(args: Array[String]): Unit = {
    println("Задание 3 b :")
    SalaryCalculator.main(args)
    println("\nЗадание 3 c :")
    SalaryDeviationCalculator.main(args)
    println("\nЗадание 3 d :")
    AdjustedSalaryCalculator.main(args)
    println("\nЗадание 3 e :")
    SalarySortedList.main(args)
    println("\nЗадание 3 f :")
    EmployeeRanking.main(args)
    println("\nЗадание 3 g :")
    MiddleLevelEmployees.main(args)
    println("\nЗадание 3 h :")
    SalaryIncrease.main(args)
  }
}


object SalaryCalculator {
  val monthlySalary: Double = {
    print("Введите годовой доход сотрудника до вычета налогов: ")
    val annualIncome = readDouble()
    print("Введите процент премии к годовому доходу: ")
    val bonusPercent = readDouble()
    print("Введите сумму компенсации за питание: ")
    val foodCompensation = readDouble()

    val totalIncome = annualIncome + (annualIncome * bonusPercent / 100) + foodCompensation
    val taxableAmount = totalIncome * 0.13 // 13% налог
    val afterTaxIncome = totalIncome - taxableAmount
    afterTaxIncome / 12
  }

  def main(args: Array[String]): Unit = {
    println(f"Месячный доход за вычетом налогов: $monthlySalary%.2f")
  }
}


object SalaryDeviationCalculator {
  import SalaryCalculator._

  val salaries = List(100000, 150000, 200000, 80000, 120000, 75000, monthlySalary)
  val averageSalary = salaries.sum / salaries.length.toDouble
  val percentageDeviations = salaries.map(salary => (salary / averageSalary - 1) * 100)

  def main(args: Array[String]): Unit = {
    println("Отклонения от среднего значения оклада на уровне всего отдела (%):")
    percentageDeviations.foreach(deviation => println(f"$deviation%.2f"))
  }
}


object AdjustedSalaryCalculator {
  import SalaryCalculator._
  import SalaryDeviationCalculator._

  def main(args: Array[String]): Unit = {
    val adjustedMonthlySalary = {
      val lastDeviation = percentageDeviations.last
      if (lastDeviation > 0) monthlySalary + 20000
      else monthlySalary - 10000
    }

    val updatedSalaries = salaries.dropRight(1) :+ adjustedMonthlySalary
    val minSalary = updatedSalaries.min
    val maxSalary = updatedSalaries.max

    println(f"Самая низкая зарплата: $minSalary%.2f")
    println(f"Самая высокая зарплата: $maxSalary%.2f")
  }
}


object SalarySortedList {
  import SalaryDeviationCalculator.salaries

  val newEmployeesSalaries = List[Double](350000, 90000)
  val updatedSalaries = salaries ++ newEmployeesSalaries
  val sortedSalaries = updatedSalaries.sorted

  def main(args: Array[String]): Unit = {
    println("Список зарплат от меньшего к большему:")
    sortedSalaries.foreach(salary => println(salary))
  }
}


object EmployeeRanking {
  import SalarySortedList.updatedSalaries

  // Так как updatedRanking теперь используется в других объектах, нужно сделать его public
  val updatedRanking: List[(Int, Double)] = { // Добавть блок инициализации
    val newEmployeeSalary = 130000
    val newUpdatedSalaries: List[Double] = updatedSalaries :+ newEmployeeSalary
    val sortedSalaries = newUpdatedSalaries.sorted

    sortedSalaries.zipWithIndex.map { case (salary, index) => (index + 1, salary) }
  }

  def main(args: Array[String]): Unit = {
    val newEmployeeSalary = 130000
    val newUpdatedSalaries: List[Double] = updatedSalaries :+ newEmployeeSalary
    val sortedSalaries = newUpdatedSalaries.sorted

    val newEmployeePosition = sortedSalaries.indexOf(newEmployeeSalary) + 1

    println("Порядковый номер нового сотрудника: " + newEmployeePosition)
    println("Обновленный отсортированный список зарплат:")

    updatedRanking.foreach { case (position, salary) => println(s"$position: $salary") }
  }
}


object MiddleLevelEmployees {
  import EmployeeRanking._

  val minMiddleSalary: Double = {
    print("Введите минимальную зарплату специалиста уровня middle: ")
    readDouble()
  }

  val maxMiddleSalary: Double = {
    print("Введите максимальную зарплату специалиста уровня middle: ")
    readDouble()
  }

  val middleLevelEmployees: List[(Int, Double)] = EmployeeRanking.updatedRanking.filter {
    case (_, salary) => salary >= minMiddleSalary && salary <= maxMiddleSalary
  }

  def main(args: Array[String]): Unit = {
    println("Сотрудники с зарплатами на уровне middle:")
    middleLevelEmployees.foreach { case (position, salary) => println(s"$position: $salary") }
  }
}


object SalaryIncrease {
  import SalarySortedList.updatedSalaries

  val increasedSalaries: List[(Int, Double, Double)] = updatedSalaries.zipWithIndex.map {
    case (salary, index) =>
      val updatedSalary = salary * 1.07
      (index + 1, salary, updatedSalary)
  }

  def main(args: Array[String]): Unit = {
    println("Порядковый номер сотрудника | старая зарплата | обновленная зарплата:")
    increasedSalaries.foreach {
      case (position, oldSalary, newSalary) =>
        println(f"$position: $oldSalary%.2f -> $newSalary%.2f")
    }
  }
}



