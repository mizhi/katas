import scala.collection.immutable.BitSet
import scala.io.Source
import scala.math._
import scala.util.Random
import scala.util.hashing.MurmurHash3
import scala.annotation.tailrec

case class BloomFilter[A <: String](capacity: Int, falseProbability: Float, bits: BitSet = BitSet.empty) {
  type HashFunction = (A => Int)

  val m: Int = computeM(capacity, falseProbability)
  val k: Int = computeK(capacity, m)

  val hashFunctions: Seq[HashFunction] = (1 to k).map { thisK => (input: A) => abs(MurmurHash3.stringHash(input * thisK)) % m }

  def addElements(elements: A*): BloomFilter[A] = this.copy(bits = bits | elements.foldLeft(BitSet.empty)(_ | hashBits(_)))
  def addElement(element: A): BloomFilter[A] = this.copy(bits = bits | hashBits(element))

  def contains(element: A): Boolean = {
    val elementBits = hashBits(element)
    (bits & elementBits) == elementBits
  }

  def hashBits(element: A): BitSet = BitSet(hashFunctions.map(hashFunc => hashFunc(element)):_*)

  def computeM(capacity: Int, falseProbability: Float): Int = ceil(-(capacity.toFloat * log(falseProbability) / pow(log(2), 2))).toInt
  def computeK(capacity: Int, m: Int): Int = ceil(m.toFloat / capacity.toFloat * log(2)).toInt
}

class Mispeller(validWords: Set[String], rng: Random) {
  val mispellingOperations = List(
    insert _,
    delete _,
    substitute _,
    transpose _
  )

  def mispell(word: String): String = {
    @tailrec
    def _mispell(word: String): String = {
      if (!validWords.contains(word)) {
        word
      } else {
        _mispell(rng.shuffle(mispellingOperations).head(word))
      }
    }
    _mispell(word)
  }

  def insert(word: String): String = {
    val where = rng.nextInt(word.length + 1)
    val (start, end) = word.splitAt(where)
    start + rng.alphanumeric.dropWhile(x => !x.isLetter).take(1).mkString + end
  }

  def delete(word: String): String = {
    val where = rng.nextInt(word.length)
    word.patch(where, "", where)
  }

  def substitute(word: String): String = {
    val where = rng.nextInt(word.length)
    word.patch(where, rng.alphanumeric.dropWhile(x => !x.isLetter).take(1).mkString, where)
  }

  def transpose(word: String): String = {
    val where = max(1, rng.nextInt(word.length))
    val (start, end) = word.splitAt(where)
    start.take(start.length - 1) + end.head + start.last + end.tail
  }
}


object BloomDriver extends App {
  def parseOptions(args: Seq[String], options: Map[String, Any]): Map[String, Any] = {
    args match {
      case "--false_prob" :: prob :: rest => parseOptions(rest, Map("false_prob" -> prob.toFloat) ++ options)
      case "--words" :: dict :: rest => parseOptions(rest, Map("words_file" -> dict) ++ options)
      case "--mispellings" :: num :: rest => parseOptions(rest, Map("num_mispellings" -> num.toInt) ++ options)
      case "--seed" :: seed :: rest => parseOptions(rest, Map("seed" -> seed.toFloat) ++ options)
      case Nil => options
      case x => {
        println(s"Unknown option ${x}")
        sys.exit(-1)
      }
    }
  }

  val options = parseOptions(args.toList, Map())

  val falseProb =  options.getOrElse("false_prob", 0.1).toString.toFloat
  val filename = options.getOrElse("words_file", "/usr/share/dict/words").toString
  val allWords = Source.fromFile(filename).getLines.map(_.trim.toLowerCase).toList
  val numMispellings = options.getOrElse("num_mispellings", 1000).toString.toInt
  val seed = options.getOrElse("seed", 42).toString.toInt

  val bloom = BloomFilter(allWords.length, falseProb).addElements(allWords:_*)
  val mispeller = new Mispeller(allWords.toSet, new Random(seed))

  val rng = new Random(seed)
  val mispelledWords = (1 to numMispellings).map(x => mispeller.mispell(allWords(rng.nextInt(allWords.length))))

  val numDetected = mispelledWords.filterNot(word => bloom.contains(word))
  println(s"${numDetected.length} out of ${mispelledWords.length}")
}

BloomDriver.main(args)
