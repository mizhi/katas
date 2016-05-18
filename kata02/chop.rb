#!/usr/bin/env ruby

require 'test/unit'
include Test::Unit::Assertions

def chop1(target, nums)
  low = 0
  high = nums.length
  while low < high do
    mid = low + (high - low) / 2
    if nums[mid] == target
      return mid
    elsif nums[mid] < target
      low = mid + 1
    else
      high = mid
    end
  end
  -1
end

def chop2(target, nums)
  -1
end

def chop3(target, nums)
  -1
end

def chop4(target, nums)
  -1
end

def chop5(target, nums)
  -1
end

def test_chop
  assert_equal(-1, yield(3, []))
  assert_equal(-1, yield(3, [1]))
  assert_equal(0,  yield(1, [1]))
  #
  assert_equal(0,  yield(1, [1, 3, 5]))
  assert_equal(1,  yield(3, [1, 3, 5]))
  assert_equal(2,  yield(5, [1, 3, 5]))
  assert_equal(-1, yield(0, [1, 3, 5]))
  assert_equal(-1, yield(2, [1, 3, 5]))
  assert_equal(-1, yield(4, [1, 3, 5]))
  assert_equal(-1, yield(6, [1, 3, 5]))
  #
  assert_equal(0,  yield(1, [1, 3, 5, 7]))
  assert_equal(1,  yield(3, [1, 3, 5, 7]))
  assert_equal(2,  yield(5, [1, 3, 5, 7]))
  assert_equal(3,  yield(7, [1, 3, 5, 7]))
  assert_equal(-1, yield(0, [1, 3, 5, 7]))
  assert_equal(-1, yield(2, [1, 3, 5, 7]))
  assert_equal(-1, yield(4, [1, 3, 5, 7]))
  assert_equal(-1, yield(6, [1, 3, 5, 7]))
  assert_equal(-1, yield(8, [1, 3, 5, 7]))
end

if __FILE__ == $0
  %i(chop1 chop2 chop3 chop4 chop5).each do |chop_method|
    puts "Testing #{chop_method}"
    begin
      test_chop(&method(chop_method))
    rescue => e
      puts "Failure in #{chop_method}, #{e.inspect}"
      puts e.backtrace
    end
  end
end
