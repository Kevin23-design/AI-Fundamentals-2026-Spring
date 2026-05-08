# 农夫(F)、白菜(C)、羊(G)、狼(W) 过河问题 - BFS 与 DFS 搜索流程打印
import collections

# 状态用左岸包含的元素集合(frozenset)来表示
START_STATE = frozenset(['F', 'C', 'G', 'W'])
GOAL_STATE = frozenset()

def to_state_str(left_bank):
    """将集合状态转换为 FCGW|| 格式的字符串以匹配图示"""
    right_bank = {'F', 'C', 'G', 'W'} - left_bank
    order = {'F': 0, 'C': 1, 'G': 2, 'W': 3}
    l_str = "".join(sorted(list(left_bank), key=lambda x: order[x]))
    r_str = "".join(sorted(list(right_bank), key=lambda x: order[x]))
    return f"{l_str}||{r_str}"

def is_valid(left_bank):
    """检查状态是否符合规则（无人看管时，狼吃羊、羊吃菜）"""
    right_bank = {'F', 'C', 'G', 'W'} - left_bank
    
    # 检查左岸
    if 'F' not in left_bank:
        if ('G' in left_bank and 'W' in left_bank) or ('C' in left_bank and 'G' in left_bank):
            return False
    # 检查右岸
    if 'F' not in right_bank:
        if ('G' in right_bank and 'W' in right_bank) or ('C' in right_bank and 'G' in right_bank):
            return False
            
    return True

def get_successors(state):
    """获取所有有效的下一步状态"""
    successors = []
    # 农夫在左岸，向右走
    if 'F' in state:
        items = [item for item in state if item != 'F']
        successors.append(state - {'F'}) # 独自过河
        for item in items:
            successors.append(state - {'F', item}) # 带一件物品过河
    # 农夫在右岸，向左走
    else:
        right_bank = {'F', 'C', 'G', 'W'} - state
        items = [item for item in right_bank if item != 'F']
        successors.append(state | {'F'}) # 独自返回
        for item in items:
            successors.append(state | {'F', item}) # 带一件物品返回
            
    # 只保留不会发生吃人/吃菜惨剧的状态
    return [s for s in successors if is_valid(s)]

def run_bfs():
    print("\n" + "="*40)
    print("开始执行 BFS 广度优先搜索 (展示队列)")
    print("="*40)
    
    queue = collections.deque([START_STATE])
    visited = {START_STATE}
    step = 1
    
    while queue:
        print(f"\n[Step {step}]")
        print(f"当前队列 Queue: {[to_state_str(s) for s in queue]}")
        
        curr = queue.popleft()
        print(f" -> 节点出队: {to_state_str(curr)}")
        
        if curr == GOAL_STATE:
            print(" -> ⭐️ 到达目标状态，搜索完成！")
            break
            
        successors = get_successors(curr)
        enqueued_any = False
        for nxt in successors:
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
                print(f"    + 扩展有效子节点: {to_state_str(nxt)} 并入队")
                enqueued_any = True
                
        if not enqueued_any:
            print("    - 无新子节点可扩展")
            
        step += 1

def run_dfs():
    print("\n" + "="*40)
    print("开始执行 DFS 深度优先搜索 (展示递归栈)")
    print("="*40)
    
    stack = []
    visited = set()
    step = [1] # 使用列表包裹以便在嵌套函数中修改
    
    def recurse(curr):
        stack.append(curr)
        visited.add(curr)
        
        print(f"\n[Step {step[0]}]")
        print(f"当前递归栈 Stack: {[to_state_str(s) for s in stack]}")
        step[0] += 1
        
        if curr == GOAL_STATE:
            print(" -> ⭐️ 到达目标状态，搜索完成！")
            return True
            
        for nxt in get_successors(curr):
            if nxt not in visited:
                # 递归调用
                if recurse(nxt):
                    return True
                    
        # 若没有找到通路，则回溯 (本题只要不乱走必定能通，不会触发此处)
        stack.pop()
        return False

    recurse(START_STATE)

if __name__ == "__main__":
    run_bfs()
    run_dfs()