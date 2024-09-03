def execute_bot(return_1, return_2, i):
    try:
        if return_1 > 0 and return_2 > 0 and i == -1:
            print("buy")
            i = i*-1
            return i
        elif return_1 < 0 and return_2 < 0 and i == 1:
            print("sell")
            i = i*-1
            return i
        else:
            print("pass")
            i = i*-1
            return i
    except Exception as e:  
        print(f"Error: {e}")
        
i = -1

result = execute_bot(1, 1, i)

print(result)