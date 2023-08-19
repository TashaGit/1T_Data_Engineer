import scala.io.StdIn.{readDouble, readLine}

object Salary {
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
    println("\nЗадание PRO 1 :")
    DisplayUpdatedSalaries.main(args)
    MarketSalary.main(args)
    println("\nЗадание PRO 2 :")
    MarketSalaryWithNames.main(args)
    println("\nЗадание PRO 3 :")
    SalaryExtremes.main(args)
    println("\nЗадание PRO 4 :")
    MarketSalaryWithoutNames.main(args)
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

  val updatedRanking: List[(Int, Double)] = {
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
  import EmployeeRanking.updatedRanking

  val increasedSalaries: List[(Int, Double, Double)] = updatedRanking.map {
    case (position, salary) =>
      val updatedSalary = salary * 1.07
      (position, salary, updatedSalary)
  }

  def main(args: Array[String]): Unit = {
    println("Порядковый номер сотрудника | старая зарплата | обновленная зарплата")
    increasedSalaries.foreach {
      case (position, oldSalary, newSalary) =>
        println(f"$position: $oldSalary%.2f -> $newSalary%.2f")
    }
  }
}

object EmployeeLevels {
  import MiddleLevelEmployees.{minMiddleSalary, maxMiddleSalary}

  def getEmployeeLevel(salary: Double): String = {
    if (salary < minMiddleSalary) "junior"
    else if (salary <= maxMiddleSalary) "middle"
    else "senior"
  }
}

object DisplayUpdatedSalaries {
  import SalaryIncrease.increasedSalaries
  import EmployeeLevels.getEmployeeLevel

  def main(args: Array[String]): Unit = {
    println("Порядковый номер сотрудника | новая зарплата | уровень специалиста")
    increasedSalaries.foreach {
      case (position, _, newSalary) =>
        val level = getEmployeeLevel(newSalary)
        println(f"$position | $newSalary%.2f | $level")
    }
  }
}

object MarketSalary {

  import SalaryIncrease.increasedSalaries
  import EmployeeLevels.getEmployeeLevel

  print("Введите среднюю зарплату специалиста уровня junior на рынке труда: ")
  val marketJuniorSalary = readDouble()
  print("Введите среднюю зарплату специалиста уровня middle на рынке труда: ")
  val marketMiddleSalary = readDouble()
  print("Введите среднюю зарплату специалиста уровня senior на рынке труда: ")
  val marketSeniorSalary = readDouble()

  val updatedEmployees: List[(Int, String, Double)] = increasedSalaries.map {
    case (position, _, newSalary) =>
      val level = getEmployeeLevel(newSalary)
      val adjustedSalary = level match {
        case "junior" if newSalary < marketJuniorSalary => marketJuniorSalary
        case "middle" if newSalary < marketMiddleSalary => marketMiddleSalary
        case "senior" if newSalary < marketSeniorSalary => marketSeniorSalary
        case _ => newSalary
      }
      (position, level, adjustedSalary)
  }

  def main(args: Array[String]): Unit = {
    println("\nПорядковый номер сотрудника | уровень специалиста | обновленная зарплата")
    updatedEmployees.foreach {
      case (position, level, adjustedSalary) =>
        println(f"$position | $level | $adjustedSalary%.2f")
    }
  }
}

object MarketSalaryWithNames {
  import MarketSalary.updatedEmployees
  val employeeNames = List("Иванов Петр", "Сидоров Максим", "Петухов Демьян",
    "Смеловкая Алиса", "Ткаченко Светлана", "Чекмарев Арсений", "Васильева Елена",
    "Пружинников Федор", "Краснова Наталия", "Круглов Семен")

  val updatedEmployeeData: List[(Int, String, String, Double)] = updatedEmployees.zip(employeeNames).map {
    case ((position, level, adjustedSalary), name) => (position, name, level, adjustedSalary)
  }

  def main(args: Array[String]): Unit = {
    println("\nТабельный номер | Фамилия Имя | Уровень специалиста | Зарплата")
    updatedEmployeeData.foreach {
      case (position, name, level, adjustedSalary) =>
        println(f"$position: $name | $level | $adjustedSalary%.2f")
    }
  }
}

object SalaryExtremes {
  import MarketSalaryWithNames.updatedEmployeeData

  val (minSalaryEmployees, maxSalaryEmployees) = {
    val minSalary = updatedEmployeeData.minBy(_._4)._4
    val maxSalary = updatedEmployeeData.maxBy(_._4)._4
    (updatedEmployeeData.filter(_._4 == minSalary), updatedEmployeeData.filter(_._4 == maxSalary))
  }

  def main(args: Array[String]): Unit = {
    println("\nСотрудники с самой низкой зарплатой:")
    minSalaryEmployees.foreach { case (_, name, _, salary) =>
      println(f"$name: $salary%.2f")
    }

    println("\nСотрудники с самой высокой зарплатой:")
    maxSalaryEmployees.foreach { case (_, name, _, salary) =>
      println(f"$name: $salary%.2f")
    }
  }
}

object MarketSalaryWithoutNames {
  import MarketSalaryWithNames.updatedEmployeeData

  def modifyName(fullName: String): String = {
    val name = fullName.split(" ")(0)
    //    val surname = fullName.split(" ")(1)
    val modifiedName = name.toLowerCase.replaceAll("[ауоыиэяюёе]", "").reverse
    s"$modifiedName"
  }

  val updatedEmployeeDataWithoutNames: List[(Int, String, String, Double)] = updatedEmployeeData.map {
    case (position, fullName, level, adjustedSalary) => (position, modifyName(fullName), level, adjustedSalary)
  }

  def main(args: Array[String]): Unit = {
    println("\nТабельный номер | Фамилия Имя | Уровень специалиста | Зарплата")
    updatedEmployeeDataWithoutNames.foreach {
      case (position, modifiedName, level, adjustedSalary) =>
        println(f"$position: $modifiedName | $level | $adjustedSalary%.2f")
    }
  }
}
